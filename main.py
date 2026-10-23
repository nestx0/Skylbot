import itertools
import logging
import os
import random
import threading
import time

import discord
from discord.ext import tasks
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from database.dataBase import *
from vicio.gacha import pullChar
from vicio.lootbox import lootbox
from vicio.views import inventory, boss
from vicio.fights import combat, setDefender
from vicio.gacha_commands import *
from juegos.blackjack.game import blackjack, jackblack
from juegos.ppt import ppt
from juegos.roulette import roulette
from other_commands import *

app = Flask(__name__)
CORS(app)

load_dotenv()
from ai.ai_funcions import ai, clear

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
lastTimeGIF = 0

tiempo_of_las_mio = 0

activities = itertools.cycle(
    [
        "🏓 Playing Ping-pong",
        "📖 Reading Documentation",
        "🔧 Repairing",
        "💤 Sleeping",
        "Filling a Token of Assistance",
    ]
)


#vicio/
#lootbox.py
bot.command(name="lootbox", help="Do you wanna test your luck with a lootbox ?")(lootbox)
#views.py
bot.command(name="inventory", help="Shows your inventory of companions")(inventory)
bot.command(name="boss", help="Fight some bosses or something")(boss)
#fights.py
bot.command(name="combat", help="Fight your friend's defender")(combat)
bot.command(name="setDefender", help="Set a defender in case someone wants to fight you")(setDefender)
#gacha.py
bot.command(name="pull", help="Get one of many characters to sell or fight with them")(pull)
bot.command(name="sell", help="Sell one or more companions for bolivares")(sell)
bot.command(name="train", help="Train a companion of your choice, with a cooldown obviously")(train)

#juegos/
#ppt.py
bot.command(name="ppt", help="Let's play rock, paper, scissors")(ppt)
#roulette.py
bot.command(name="roulette", help="A classic game of roulette with some options")(roulette)
#blackjack/game.py
bot.command(name="blackjack", help="Play a classic Blackjack hand using points as bets")(blackjack)
bot.command(name="jackblack", help="Too good to be true")(jackblack)

#ai/ai_functions.py
bot.command(name="ai", help="Ask Skylbot about anything, it will answer")(ai)
bot.command(name="clear", help="Make Skylbot forget what you told it")(clear)

#other_commands.py
bot.command(name="guide", help="Kinda self-explanatory")(guide)
bot.command(name="ping", help="pong")(ping)
bot.command(name="poll", help="Quick question about anything")(poll)
bot.command(name="joke", help="Random joke, go!")(joke)
bot.command(name="work", help="Get some points to bet on Blackjack")(work)
bot.command(name="pay", help="Pay an amount to another member")(pay)
bot.command(name="balance", help="Check your current balance")(balance)
bot.command(name="leaderboard", help="Get the top 10 members with the most points")(leaderboard)
bot.command(name="mine", help="Grab a reward if you're quick enough")(mine)
bot.command(name="buyRole", help="Secret role for 200k")(buyRole)


@bot.event
async def on_ready():
    change_activity.start()
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
            await message.channel.send(
                file=discord.File("assets/image0.gif")
            )

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