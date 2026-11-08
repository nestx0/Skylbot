"""API local de Alosu sobre Flask y la base SQLite de Skylbot.

Discord autoriza al inicio. Las operaciones posteriores usan la sesión de
Flask, no un user_id enviado por el cliente. Sin servidor Node ni proxy HTTP
hacia la API de Skylbot. La interfaz web sí necesita HTTPS accesible por Discord.
"""

from __future__ import annotations

import copy
import json
import os
import random
import secrets
import sqlite3
import threading
import time
from functools import wraps
from contextlib import contextmanager
from pathlib import Path
from math import isfinite
from urllib import error, parse, request as urlrequest

from flask import Blueprint, Flask, jsonify, request, send_from_directory, session

ROOT = Path(__file__).resolve().parents[1]
CLIENT_DIST = Path(__file__).resolve().parent / "client" / "dist"
SESSION_DURATION = 12 * 3600
GACHA_COST = 3_000
RARE = {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 4, "Legendary": 5}

bp = Blueprint("alosu", __name__)
_games: dict[str, dict] = {}
_sessions: dict[str, dict] = {}
_game_lock = threading.Lock()
_score_lock = threading.Lock()


def _error(message: str, status: int):
    return jsonify({"error": message}), status


def _user():
    return session.get("alosu_user")


def _identity_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not _user():
            return _error("Sesión de Discord no iniciada", 401)
        return fn(*args, **kwargs)
    return wrapper


def _discord_json(url: str, access_token: str) -> dict:
    req = urlrequest.Request(url, headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"})
    with urlrequest.urlopen(req, timeout=8) as resp:
        return json.load(resp)


def _exchange_token(code: str) -> dict:
    client_id = os.environ.get("DISCORD_CLIENT_ID", "")
    secret = os.environ.get("DISCORD_CLIENT_SECRET", "")
    if not client_id or not secret:
        raise RuntimeError("Se requieren DISCORD_CLIENT_ID y DISCORD_CLIENT_SECRET")
    body = parse.urlencode({"client_id": client_id, "client_secret": secret, "grant_type": "authorization_code", "code": code}).encode()
    req = urlrequest.Request("https://discord.com/api/oauth2/token", body, {"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urlrequest.urlopen(req, timeout=10) as resp:
        return json.load(resp)


@bp.post("/api/token")
def exchange_discord_token():
    data = request.get_json(silent=True) or {}
    code = data.get("code")
    if not isinstance(code, str) or not 3 <= len(code) <= 3000:
        return _error("Código OAuth inválido", 400)
    try:
        tokens = _exchange_token(code)
        token = tokens.get("access_token")
        if not token:
            return _error("Discord no ha autorizado la aplicación", 401)
        profile = _discord_json("https://discord.com/api/users/@me", token)
        uid = profile.get("id")
        if not isinstance(uid, str) or not uid.isdigit():
            return _error("Identidad de Discord inválida", 401)
        session.clear()
        session["alosu_user"] = uid
        session["alosu_name"] = str(profile.get("username", "Discord User"))[:100]
        session["alosu_avatar"] = profile.get("avatar")
        session.permanent = True
        return jsonify({"access_token": token})
    except (error.URLError, ValueError, TimeoutError, OSError):
        return _error("No se pudo autenticar mediante Discord", 502)
    except RuntimeError:
        return _error("Configuración OAuth incompleta", 503)


@bp.get("/api/alosu/me")
@_identity_required
def me():
    return jsonify({"id": _user(), "username": session.get("alosu_name")})


@bp.get("/api/alosu/health")
def health():
    return jsonify({"status": "ok", "component": "alosu"})


@contextmanager
def _open_db():
    path = Path(os.environ.get("SKYLBOT_DB", str(ROOT / "bot.db")))
    con = sqlite3.connect(path, timeout=15)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _inventory_from_db(raw) -> list:
    value = raw or "[]"
    for _ in range(3):
        if not isinstance(value, str):
            break
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return value if isinstance(value, list) else []


def _user_row(con, uid: str):
    con.execute("INSERT OR IGNORE INTO users (user_id, balance, inventory) VALUES (?, 0, '[]')", (uid,))
    return con.execute("SELECT balance, inventory FROM users WHERE user_id = ?", (uid,)).fetchone()


@bp.get("/api/alosu/balance")
@_identity_required
def get_balance():
    with _open_db() as con:
        row = _user_row(con, _user())
        return jsonify({"balance": int(row["balance"]), "fallback": False})


@bp.get("/api/alosu/all_users")
@_identity_required
def all_users():
    # Conserva el formato esperado por Warehouse; autenticación una vez por sesión.
    with _open_db() as con:
        rows = con.execute("SELECT * FROM users").fetchall()
        return jsonify([dict(row) for row in rows])


def _random_character():
    from vicio.personajes import personajesComun, personajesEpico, personajesRaro, personajesUncommon
    rarity = random.randint(0, 100)
    pool = personajesComun
    if 60 < rarity <= 85:
        pool = personajesUncommon
    elif 85 < rarity <= 95:
        pool = personajesRaro
    elif rarity > 95:
        pool = personajesEpico
    return copy.deepcopy(random.choice(pool))


def _rolls(con, uid: str, count: int) -> tuple[list[dict], int]:
    from vicio.gacha import Character, lvlUP
    row = _user_row(con, uid)
    price = count * GACHA_COST
    balance = int(row["balance"])
    if balance < price:
        raise ValueError(f"Saldo insuficiente: {balance} < {price}")
    inventory = _inventory_from_db(row["inventory"])
    results = []
    for _ in range(count):
        char = Character(_random_character())
        old = next((item for item in inventory if isinstance(item, dict) and item.get("id") == char.id), None)
        is_new = old is None
        if old:
            char = lvlUP(Character(copy.deepcopy(old)))
            old.update(char.toDICT())
        else:
            inventory.append(char.toDICT())
        result = char.toDICT()
        rarity = RARE.get(result["rarity"], 1)
        image = str(result.get("image", "")).split("/")[-1]
        results.append({
            **result,
            "index": len(results) + 1,
            "rarity": rarity,
            "element": "",
            "isNew": is_new,
            "stars": "★" * rarity,
            "image": f"/api/alosu/proxy-image/{image}",
        })
    new_balance = balance - price
    con.execute("UPDATE users SET balance = ?, inventory = ? WHERE user_id = ?", (new_balance, json.dumps(inventory, ensure_ascii=False), uid))
    return results, new_balance


@bp.post("/api/alosu/gacha/pull")
@_identity_required
def gacha_pull():
    body = request.get_json(silent=True) or {}
    amount = body.get("amount", 1)
    if not isinstance(amount, int) or isinstance(amount, bool) or amount not in (1, 10):
        return _error("Solo se permite una tirada o diez", 400)
    try:
        with _open_db() as con:
            con.execute("BEGIN IMMEDIATE")
            results, balance = _rolls(con, _user(), amount)
        return jsonify({
            "status": "success",
            "pulls": amount,
            "results": results,
            "summary": {"new_balance": balance, "total_cost": amount * GACHA_COST,
                        "pity5": 0, "pity4": 0, "goldCount": 0},
        })
    except ValueError as exc:
        return jsonify({"status": "error", "error": "insufficient_funds", "message": str(exc)}), 400


@bp.get("/api/alosu/proxy-image/<path:filename>")
@_identity_required
def character_image(filename: str):
    # No hay solicitudes a GitHub: se sirven los assets locales de Skylbot.
    if "/" in filename or "\\" in filename:
        return _error("Nombre de imagen inválido", 400)
    return send_from_directory(ROOT / "assets" / "characters", filename)


# Blackjack heredado: endpoints para el cliente modular; el juego activo
# actualmente utiliza su propia lógica en game2.ts.
SUITS = ["♠", "♥", "♣", "♦"]
VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def _draw(deck):
    return deck.pop()


def _score(cards):
    score = sum(c["weight"] for c in cards)
    aces = sum(c["value"] == "A" for c in cards)
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score


def _get_game(data):
    game = _games.get(data.get("gameId"))
    if not game or game["userId"] != _user() or game["gameState"] != "playing":
        return None
    return game


@bp.post("/api/alosu/blackjack/start")
@_identity_required
def blackjack_start():
    deck = [{"suit": suit, "value": value,
             "weight": 11 if value == "A" else 10 if value in ("J", "Q", "K") else int(value)}
            for suit in SUITS for value in VALUES]
    random.shuffle(deck)
    player = [_draw(deck), _draw(deck)]
    dealer = [_draw(deck), _draw(deck)]
    gid = "bj_" + secrets.token_urlsafe(18)
    initial_21 = _score(player) == 21
    with _game_lock:
        _games[gid] = {"userId": _user(), "deck": deck, "player": player,
                       "dealer": dealer, "gameState": "gameover" if initial_21 else "playing", "time": time.monotonic()}
    return jsonify({"gameId": gid, "playerHand": player, "dealerHand": dealer[:1],
                    "playerScore": _score(player), "gameState": "gameover" if initial_21 else "playing",
                    "isBlackjack": initial_21, "serverSync": True, "timestamp": int(time.time() * 1000)})


@bp.post("/api/alosu/blackjack/hit")
@_identity_required
def blackjack_hit():
    data = request.get_json(silent=True) or {}
    with _game_lock:
        game = _get_game(data)
        if not game:
            return _error("Partida no válida", 400)
        if time.monotonic() - game["time"] > 1800:
            return _error("Partida caducada", 400)
        card = _draw(game["deck"])
        game["player"].append(card)
        game["time"] = time.monotonic()
        score = _score(game["player"])
        if score > 21:
            game["gameState"] = "gameover"
    return jsonify({"card": card, "playerScore": score,
                    "busted": score > 21, "gameState": game["gameState"], "serverSync": True})


@bp.post("/api/alosu/blackjack/stand")
@_identity_required
def blackjack_stand():
    data = request.get_json(silent=True) or {}
    with _game_lock:
        game = _get_game(data)
        if not game:
            return _error("Partida no válida", 400)
        dealt = []
        while _score(game["dealer"]) < 17:
            card = _draw(game["deck"])
            game["dealer"].append(card)
            dealt.append(card)
        player_score, dealer_score = _score(game["player"]), _score(game["dealer"])
        if dealer_score > 21 or player_score > dealer_score:
            result = {"message": "You Won! (+3)", "win": True, "points": 3}
        elif player_score < dealer_score:
            result = {"message": "You Lost (-2)", "win": False, "points": -2}
        else:
            result = {"message": "Push (+1)", "win": False, "points": 1}
        game["gameState"] = "gameover"
    return jsonify({"dealerHand": game["dealer"], "dealerCards": dealt,
                    "dealerScore": dealer_score, "result": result, "gameState": "gameover", "serverSync": True})


def _scores_path():
    state_dir = Path(os.environ.get("ALOSU_RUNTIME_DIR", str(ROOT / "alosu" / "runtime")))
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "leaderboard.json"


def _read_scores():
    try:
        scores = json.loads(_scores_path().read_text(encoding="utf-8"))
        return scores if isinstance(scores, list) else []
    except (OSError, ValueError):
        return []


@bp.get("/api/alosu/leaderboard")
@_identity_required
def leaderboard():
    with _score_lock:
        return jsonify(sorted(_read_scores(), key=lambda x: x.get("score", 0), reverse=True)[:50])


@bp.post("/api/alosu/score")
@_identity_required
def update_score():
    data = request.get_json(silent=True) or {}
    raw = data.get("score")
    if type(raw) not in (int, float) or not isfinite(raw) or not -1_000_000 <= raw <= 1_000_000_000:
        return _error("Puntuación inválida", 400)
    user_id = _user()
    with _score_lock:
        scores = _read_scores()
        scores = [u for u in scores if u.get("userId") != user_id]
        scores.append({"userId": user_id, "username": session.get("alosu_name"),
                       "avatarUrl": None, "score": int(raw)})
        path = _scores_path()
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(scores, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(path)
    return jsonify({"success": True})


@bp.post("/api/alosu/game-complete")
@_identity_required
def game_complete():
    data = request.get_json(silent=True) or {}
    sid = data.get("sessionId")
    if not isinstance(sid, str) or len(sid) > 200 or not sid:
        return _error("Se requiere sessionId", 400)
    with _game_lock:
        _sessions[sid] = {"sessionId": sid, "userId": _user(), "completed": True,
                          "characters": data.get("characters", 0), "endTime": int(time.time() * 1000)}
    return jsonify({"success": True, "sessionId": sid})


@bp.get("/alosu/")
@bp.get("/alosu/<path:filename>")
def activity_files(filename="index.html"):
    # La autenticación del API está protegida; el cliente estático puede cargar.
    if not CLIENT_DIST.is_dir():
        return "No se ha compilado el cliente. Ejecuta el build indicado en alosu/README.md", 503
    candidate = CLIENT_DIST / filename
    if candidate.is_file():
        return send_from_directory(CLIENT_DIST, filename)
    return send_from_directory(CLIENT_DIST, "index.html")


def register_alosu(app: Flask) -> None:
    secret = os.environ.get("ALOSU_SESSION_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("Falta ALOSU_SESSION_SECRET (32 caracteres o más). No se inicia la actividad sin sesiones seguras.")
    app.secret_key = secret
    app.config.update(SESSION_COOKIE_NAME="skylbot_alosu", SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=os.environ.get("ALOSU_DEV_INSECURE_COOKIE") != "1",
                      PERMANENT_SESSION_LIFETIME=SESSION_DURATION)

    @app.before_request
    def alosu_same_origin():
        # Las APIs antiguas modificaban saldos con un user_id suministrado por
        # el navegador. No se usan en Alosu y se desactivan por defecto.
        unsafe_legacy = (request.path in ("/api/balance/deposit", "/api/balance/withdraw")
                         or request.path.startswith("/api/gacha/pull/")
                         or request.path.startswith("/api/gacha/tenpull/"))
        if unsafe_legacy and os.environ.get("SKYLBOT_ENABLE_LEGACY_API") != "1":
            return _error("Endpoint antiguo deshabilitado: utiliza Alosu API", 410)
        if request.method in ("POST", "PUT", "PATCH", "DELETE") and (request.path.startswith("/api/alosu/") or request.path == "/api/token"):

            origin = request.headers.get("Origin", "")
            # Browser sends Origin on same-origin fetch; reject cross-origin writes.
            if origin:
                try:
                    host = parse.urlsplit(origin).netloc
                    dev_origin = os.environ.get("ALOSU_DEV_INSECURE_COOKIE") == "1" and host in ("localhost:3000", "127.0.0.1:3000")
                    # Discord sirve la actividad mediante <application_id>.discordsays.com;
                    # esa cabecera Origin no siempre coincide con el Host que ve Flask.
                    discord_client_id = os.environ.get("DISCORD_CLIENT_ID", "")
                    discord_origin = bool(discord_client_id) and host == f"{discord_client_id}.discordsays.com"
                    extra_origin = os.environ.get("ALOSU_ALLOWED_ORIGIN", "")
                    configured_origin = bool(extra_origin) and origin.rstrip("/") == extra_origin.rstrip("/")
                    if host != request.host and not dev_origin and not discord_origin and not configured_origin:
                        return _error("Origen no permitido", 403)
                except ValueError:
                    return _error("Origen inválido", 403)
        return None

    app.register_blueprint(bp)
