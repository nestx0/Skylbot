import itertools
import logging
import os
import random
import threading
import time

import discord
from discord.ext import tasks
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from database.dataBase import *
from database.plantsDatabase import PlantsDatabase
from juegos.blackjack.game import blackjack, jackblack
from juegos.ppt import ppt
from juegos.roulette import roulette
from other_commands import *
from plants.plantsCommands import plantinv, sellplant, shop, water
from vicio.fights import combat, setDefender
from vicio.gacha import pullChar
from vicio.gacha_commands import *
from vicio.lootbox import lootbox
from vicio.views import boss, inventory

app = Flask(__name__)
CORS(app)
load_dotenv()

from ai.ai_funcions import ai, clear
from alosu import register_alosu

register_alosu(app)
token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
lastTimeGIF = 0
tiempo_of_las_mio = 0

activities = itertools.cycle(
    [
        "🏓 Playing Ping-pong",
        "📖 Reading Documentation",
        "Sleeping",
        "Filling a Token of Assistance",
        "Fighting Somali Pirates",
        "Destroying fascism",
    ]
)


# vicio/
# lootbox.py
bot.command(name="lootbox", help="Do you wanna test your luck with a lootbox ?")(
    lootbox
)
# views.py
bot.command(name="inventory", help="Shows your inventory of companions")(inventory)
bot.command(name="boss", help="Fight some bosses or something")(boss)
# fights.py
bot.command(name="combat", help="Fight your friend's defender")(combat)
bot.command(
    name="setDefender", help="Set a defender in case someone wants to fight you"
)(setDefender)
# gacha.py
bot.command(name="pull", help="Get one of many characters to sell or fight with them")(
    pull
)
bot.command(name="sell", help="Sell one or more companions for bolivares")(sell)
bot.command(
    name="train", help="Train a companion of your choice, with a cooldown obviously"
)(train)

# juegos/
# ppt.py
bot.command(name="ppt", help="Let's play rock, paper, scissors")(ppt)
# roulette.py
bot.command(name="roulette", help="A classic game of roulette with some options")(
    roulette
)
# blackjack/game.py
bot.command(
    name="blackjack", help="Play a classic Blackjack hand using points as bets"
)(blackjack)
bot.command(name="jackblack", help="Too good to be true")(jackblack)

# ai/ai_functions.py
bot.command(name="ai", help="Ask Skylbot about anything, it will answer")(ai)
bot.command(name="clear", help="Make Skylbot forget what you told it")(clear)

# other_commands.py
bot.command(name="guide", help="Kinda self-explanatory")(guide)
bot.command(name="ping", help="pong")(ping)
bot.command(name="poll", help="Quick question about anything")(poll)
bot.command(name="joke", help="Random joke, go!")(joke)

# Economy commands
bot.command(name="work", help="Get some points to bet on Blackjack")(work)
bot.command(name="pay", help="Pay an amount to another member")(pay)
bot.command(name="balance", help="Check your current balance")(balance)
bot.command(name="leaderboard", help="Get the top 10 members with the most points")(
    leaderboard
)
bot.command(name="mine", help="Grab a reward if you're quick enough")(mine)
bot.command(name="buyRole", help="Secret role for 200k")(buyRole)

# Plants Commands (plants/)

bot.command(name="shop", help="Open the daily seed shop")(shop)
bot.command(name="plantinv", help="Check your plant inventory")(plantinv)
bot.command(name="water", help="Water a plant to grow it or germinate a seed")(water)
bot.command(name="sellplant", help="Sell a plant for bolivares")(sellplant)

COMMAND_HELP = {
    "ai": "Ask Skylbot a question.\nUsage: *ai <question>\nExample: *ai What is a black hole?",
    "balance": "Check your current balance.\nUsage: *balance",
    "blackjack": (
        "Play Blackjack with a bet.\n"
        "Usage: *blackjack <amount|all|max|allin>\n"
        "Examples: *blackjack 100 | *blackjack allin\n"
        "all, max and allin bet your entire available balance."
    ),
    "boss": (
        "Browse bosses or fight one with your character.\n"
        "Usage: *boss list | *boss fight <boss_slot> <character_slot>\n"
        "Examples: *boss list | *boss fight 1 2"
    ),
    "buyRole": "Purchase the secret role for 200,000 bolivares.\nUsage: *buyRole",
    "clear": "Clear Skylbot's current AI conversation context.\nUsage: *clear",
    "combat": (
        "Challenge another member to character combat.\n"
        "Usage: *combat @member <amount|all|max|allin> <character_slot>\n"
        "Examples: *combat @friend 100 1 | *combat @friend allin 1\n"
        "all, max and allin use your full available balance as the bet."
    ),
    "guide": "Show an alphabetically sorted command summary.\nUsage: *guide\nFor detailed help, use *help <command>.",
    "inventory": "Browse your character inventory.\nUsage: *inventory\nThe displayed pages show slot positions.",
    "jackblack": "Send a Jack Black GIF.\nUsage: *jackblack <text>\nExample: *jackblack hi",
    "joke": "Get a random joke.\nUsage: *joke",
    "leaderboard": "Show the ten richest members.\nUsage: *leaderboard",
    "lootbox": "Open a lootbox for 10,000 bolivares.\nUsage: *lootbox",
    "mine": "Claim a temporary free reward when it appears.\nUsage: *mine",
    "pay": (
        "Transfer bolivares to another member.\n"
        "Usage: *pay @member <amount|all|max>\n"
        "Examples: *pay @friend 100 | *pay @friend all | *pay @friend max\n"
        "all and max transfer your entire available balance."
    ),
    "ping": "Check whether Skylbot responds.\nUsage: *ping",
    "plantinv": "Browse your plant and seed inventory.\nUsage: *plantinv",
    "poll": "Create a poll with reaction options.\nUsage: *poll <question>\nExample: *poll Should we play tonight?",
    "ppt": (
        "Play Rock, Paper, Scissors, solo or against another member.\n"
        "Usage: *ppt <amount|all|max|allin>\n"
        "       *ppt @member <amount|all|max|allin>\n"
        "Examples: *ppt 100 | *ppt @friend allin\n"
        "all, max and allin bet your entire available balance."
    ),
    "pull": (
        "Get random collectible characters for 3,000 bolivares per pull.\n"
        "Usage: *pull [quantity|all|max]\n"
        "Examples: *pull | *pull 1 | *pull 10 | *pull all | *pull max\n"
        "Without arguments, pulls once. all and max use as many pulls as you can afford."
    ),
    "roulette": (
        "Bet on a roulette result.\n"
        "Usage: *roulette <amount|all|max|allin> <choice> [numbers]\n"
        "Examples: *roulette 100 red | *roulette max black | *roulette 100 numbers 7 12 20\n"
        "Choices: red, black, green, 1st, 2nd, 3rd, half1, half2, "
        "orphans, gserie, 5/8, zerozone, numbers.\n"
        "all, max and allin bet your entire available balance."
    ),
    "sell": (
        "Sell one or more characters from your inventory.\n"
        "Usage: *sell <slot ...|all|max>\n"
        "Examples: *sell 1 | *sell 1 3 5 | *sell all | *sell max\n"
        "Slot numbers may be separated by spaces. all and max sell all characters."
    ),
    "sellplant": (
        "Sell one or more grown plants, not seeds.\n"
        "Usage: *sellplant <slot ...|all|max>\n"
        "Examples: *sellplant 1 | *sellplant 1 3 5 | *sellplant all\n"
        "all and max sell all grown plants, leaving seeds in your inventory."
    ),
    "setDefender": (
        "Choose a character as your combat defender.\n"
        "Usage: *setDefender <character_slot>\n"
        "Example: *setDefender 2"
    ),
    "shop": "Browse the seed shop and buy seeds using its buttons.\nUsage: *shop",
    "train": (
        "Train one character (one-hour user cooldown).\n"
        "Usage: *train <character_slot>\nExample: *train 1"
    ),
    "water": (
        "Water plants or germinate seeds in your plant inventory.\n"
        "Usage: *water <slot ...|all|max>\n"
        "Examples: *water 1 | *water 1 3 5 | *water all\n"
        "all and max process every slot. A plant can only be watered once per day."
    ),
    "work": "Earn a small reward (one-minute user cooldown).\nUsage: *work",
}

for command_name, description in COMMAND_HELP.items():
    command = bot.get_command(command_name)
    if command is not None:
        command.help = description
        command.brief = description.splitlines()[0]


@bot.event
async def on_ready():
    change_activity.start()
    PlantsDatabase.create_table()
    assert bot.user is not None
    print(f"We are ready to go, {bot.user.name}")


@tasks.loop(seconds=240)
async def change_activity():
    next_status = next(activities)
    await bot.change_presence(activity=discord.Game(next_status))


@bot.event
async def on_member_join(member):
    canalBienvenida = 1397875243661529230
    canal = member.guild.get_channel(canalBienvenida)

    if canal:
        await canal.send(f"Welcome {member.mention}, why did you do this")
        await canal.send(file=discord.File("assets/IMG_6372.webp"))
    else:
        print("Channel not found")


@bot.event
async def on_message(message):

    global lastTimeGIF, tiempo_of_las_mio

    now = time.time()
    peruano = random.randint(1, 500)

    if message.author == bot.user:
        return

    if peruano == 69:
        return await message.channel.send("Silencio peruano")

    if not mio_estado["activo"] and peruano == 420:
        mio_estado["activo"] = True
        mio_estado["reclamado"] = False
        tiempo_of_las_mio = now
        await message.channel.send(
            "🎁 ¡Free bolivares! The first one to write *mine obtains the reward. 🎁"
        )

    if (
        mio_estado["activo"]
        and not mio_estado["reclamado"]
        and now - tiempo_of_las_mio > 30
    ):
        mio_estado["activo"] = False
        await message.channel.send("⏱️ No one claimed ")

    if "nigga" in message.content.lower():
        await message.delete()
        if now - lastTimeGIF >= 30:
            lastTimeGIF = now
            await message.channel.send(file=discord.File("assets/image0.gif"))

    if message.type == discord.MessageType.new_member:
        await message.delete()

    await bot.process_commands(message)


@app.route("/api/all_users", methods=["GET"])
def api_get_users():
    try:
        users = getAllUsers()
        print("Usuarios obtenidos")
        return jsonify(users), 200
    except Exception as e:
        print("Error obteniendo los usuarios")
        return jsonify({"error": str(e)}), 500


@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = getUser(user_id)
        print("Usuario conseguido")
        return jsonify(user), 200
    except Exception as e:
        print("Error obteniendo al user")
        return jsonify({"error": str(e)}), 500


@app.route("/api/balance/<int:user_id>", methods=["GET"])
def get_balance(user_id):
    try:
        balance = int(getUser(user_id)["balance"])
        return jsonify(balance), 200
    except Exception as e:
        print("Algo mal al conseguir el balance")
        return jsonify({"error": str(e)}), 500


@app.route("/api/balance/withdraw", methods=["POST"])
def withdrawMoney():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        amount = data.get("amount")

        if not user_id or amount is None:
            return jsonify({"error": "Faltan datos (user_id o amount)"}), 400

        if amount <= 0:
            return jsonify({"error": "La cantidad debe ser mayor a 0"}), 400

        user = getUser(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        balance = int(user["balance"])

        if balance < amount:
            return jsonify({"error": "Saldo insuficiente"}), 400

        balance -= amount
        updateUser(user_id, balance)

        return jsonify({"nuevo_balance": balance, "status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500


@app.route("/api/balance/deposit", methods=["POST"])
def depositMoney():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        amount = data.get("amount")

        if not user_id or amount is None:
            return jsonify({"error": "Faltan datos (user_id o amount)"}), 400

        if amount <= 0:
            return jsonify({"error": "La cantidad debe ser mayor a 0"}), 400

        user = getUser(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        balance = int(user["balance"])

        balance += amount
        updateUser(user_id, balance)

        return jsonify({"nuevo_balance": balance, "status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500


# @app.route("/api/update_user/<int:user_id>", methods=["GET"])
# def update_balance(user_id):
#    try:
#        balance = int(getUser(user_id)["balance"])
#        updateUser(user_id, balance - 1)
#        return jsonify({"resp": "Todo bien"}), 500
#    except Exception as e:
#        print("Algo mal actualizando")
#        return jsonify({"error": str(e)}), 500
@app.route("/api/gacha/pull/<int:userID>", methods=["GET"])
def api_pull(userID):
    try:
        balance = int(getUser(userID)["balance"])

        if balance < 3000:
            return jsonify({"error": "not enough bolivares"}), 400
        balance -= 3000
        updateUser(userID, balance)
        char = pullChar(userID)
        dictChar = char.toDICT()
        return jsonify(
            {"status": "success", "character": dictChar, "new_balance": balance}
        ), 200
    except Exception as e:
        print("Algo mal con la tirada")
        return jsonify({"error": str(e)}), 500


@app.route("/api/gacha/tenpull/<int:userID>", methods=["GET"])
def api_ten_pull(userID):
    try:
        balance = int(getUser(userID)["balance"])

        if balance < 30000:
            return jsonify({"error": "not enough bolivares"}), 400

        balance -= 30000
        updateUser(userID, balance)
        listChar = []
        for i in range(10):
            char = pullChar(userID)
            listChar.append(char.toDICT())
        return jsonify(
            {"status": "success", "character": listChar, "new_balance": balance}
        ), 200
    except Exception as e:
        print("Algo mal con la tirada")
        return jsonify({"error": str(e)}), 500


def run_api():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if token is not None:
    t = threading.Thread(target=run_api, daemon=True)
    t.start()
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
