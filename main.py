import asyncio
import itertools
import logging
import os
import random
import threading
import time

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from jokeapi import Jokes
from zai import ZhipuAiClient

from ai.ai_funcions import prompt_inicial
from juegos.blackjack.game import BlackjackGame
from juegos.blackjack.views import BlackjackView
from database.dataBase import *
from juegos.ppt.ppt_view import PPTView
from juegos.roulette.roulette import *
from vicio.bosses import bosses, bossHandler
from vicio.fights import fight
from vicio.gacha import *
from vicio.lootbox import *
from vicio.rewards import *
from vicio.views import BossListView, InventoryView
from ai.colaIA import GlobalQueue, TextBlock

app = Flask(__name__)
CORS(app)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
aiKey = os.getenv("AI_TOKEN")
ai_lock = asyncio.Lock()
history = GlobalQueue()
client = ZhipuAiClient(api_key=aiKey)
model = "glm-5.3-flash"

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()

intents.message_content = True
intents.members = True

lastTimeGIF = 0

mio_activo = False
mio_reclamado = False
tiempo_of_las_mio = 0

bot = commands.Bot(command_prefix="*", intents=intents)

activities = itertools.cycle(
    ["🏓 Playing Ping-pong", "📖 Reading Documentation", "🔧 Repairing", "💤 Sleeping"]
)


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

    global lastTimeGIF, mio_activo, mio_reclamado, tiempo_of_las_mio

    now = time.time()
    peruano = random.randint(1, 500)

    if message.author == bot.user:
        return
        #    if client.user.mentioned_in(message):

        # ai()

    if peruano == 69:
        return await message.channel.send("Silencio peruano")

    if mio_activo == False and peruano == 420:
        mio_activo = True
        mio_reclamado = False
        tiempo_of_las_mio = now
        await message.channel.send(
            "🎁 ¡Free bolivares! The first one to write *mine obtains the reward. 🎁"
        )

    if mio_activo and not mio_reclamado and now - tiempo_of_las_mio > 30:
        mio_activo = False
        await message.channel.send("⏱️ No one claimed ")

    if "nigga" in message.content.lower():
        await message.delete()
        if now - lastTimeGIF >= 30:
            lastTimeGIF = now
            await message.channel.send(file=discord.File("assets/image0.gif"))

    if message.type == discord.MessageType.new_member:
        await message.delete()

    await bot.process_commands(message)


@bot.command(help="pong")
async def ping(ctx):
    await ctx.send("**pong**")


@bot.command(help="Quick question about anything")
async def poll(ctx, *, msg):

    emojiID = 1377357089801896076
    emojiID2 = 1377298954865086494

    customEmoji1 = bot.get_emoji(emojiID)
    customEmoji2 = bot.get_emoji(emojiID2)

    embed = discord.Embed(title="Rapid Question", description=msg)

    await ctx.message.delete()

    poll_msg = await ctx.send(embed=embed)
    if customEmoji1 and customEmoji2:
        await poll_msg.add_reaction(customEmoji1)
        await poll_msg.add_reaction(customEmoji2)
    else:
        print("Emojis not found")


@bot.command(help="Random joke, go!")
async def joke(ctx):
    j = await Jokes()
    joke = await j.get_joke()

    msg = ""

    if joke["type"] == "single":
        msg = joke["joke"]
    else:
        msg = joke["setup"]
        msg += "\n"
        msg += f"||{joke['delivery']}||"
    await ctx.send(msg)


@bot.command(help="Play a classic Blackjack hand using points as bets")
async def blackjack(ctx, bet):

    balance = int(getUser(ctx.author.id)["balance"])
    file = discord.File("assets/Duala_dealer.webp", filename="Duala_dealer.webp")

    if isinstance(bet, str) and bet.lower() == "allin":
        bet = balance
    else:
        try:
            bet = int(bet)
            if bet < 1:
                return await ctx.send("❌ You must bet at least 1 point.")
        except ValueError:
            return await ctx.send("❌ You must enter a number or 'allin'.")
    if bet > balance:
        return await ctx.send("❌ Not enough balance.")

    updateUser(ctx.author.id, balance - bet)

    game = BlackjackGame(ctx.author, bet)
    view = BlackjackView(game)
    await ctx.send(embed=game.generarEmbed(), view=view, file=file)

    balance += bet


@bot.command(help="Get some points to bet on Blackjack")
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    userID = ctx.author.id
    userBalance = getUser(userID)

    reward = random.randint(350, 500)
    newBalance = userBalance["balance"] + reward

    updateUser(userID, newBalance)

    await ctx.send(f"You've earned {reward}, your balance is {newBalance}")


@bot.command(help="Check your current balance")
async def balance(ctx):
    balance = getUser(ctx.author.id)["balance"]
    mensaje = ""

    if balance == 0:
        mensaje = ", you're fucking broke"

    await ctx.send(f"Your current balance is {balance}{mensaje}")


@bot.command(help="Kinda self-explanatory")
async def guide(ctx):

    lines = []
    for cmd in bot.commands:
        signature = f"{cmd.signature}" if cmd.signature else ""
        description = cmd.help or "No description yet"
        lines.append(f"• **{cmd.name} {signature}** -   {description}")
    listado = "\n".join(lines)

    embed = discord.Embed(
        title="Commands", description=listado, color=discord.Color.green()
    )

    await ctx.send(embed=embed)


@bot.command(help="Get the top 10 members with the most points")
async def leaderboard(ctx):
    entries = []
    leaderboard = getLeaderboard()

    for i, entry in enumerate(leaderboard, start=1):
        member = ctx.guild.get_member(entry["user_id"])
        if member:
            name = member.display_name
            entries.append(f"{i}. **{name}** - {entry['balance']} bolivares")
    msg = "\n".join(entries)

    embed = discord.Embed(
        title="Leaderboard", description=msg, color=discord.Color.green()
    )

    await ctx.send(embed=embed)


@bot.command(help="Too good to be true")
async def jackblack(ctx, *, msg):
    await ctx.send(file=discord.File("assets/jack-black-minecraft.gif"))


@bot.command(help="Pay an amount to another member")
async def pay(ctx, member: discord.Member, amount: int):
    user_id = member.id
    balance = getUser(ctx.author.id)["balance"]

    if user_id == ctx.author.id or amount < 1:
        await ctx.send("How are you supposed to do that")
        return

    if balance < amount:
        await ctx.send(f"You're poor, your maximum balance is {balance}")
    else:
        balance -= amount
        otherBalance = getUser(user_id)["balance"]
        updateUser(ctx.author.id, balance)
        updateUser(user_id, otherBalance + amount)
        await ctx.send(f"Succesfully sent {amount} to {member.display_name}")


@bot.command(help="A classic game of roulette with some options")
async def roulette(ctx, amount=None, choice=None, *, numbers: str | None = None):

    balance = getUser(ctx.author.id)["balance"]
    numbas = getNumbers()
    if isinstance(amount, str) and amount.lower() == "allin":
        amount = balance
    else:
        try:
            amount = int(amount)
            if amount < 1:
                return await ctx.send("❌ You must bet at least 1 point.")
        except ValueError:
            return await ctx.send("❌ You must enter a number or 'allin'.")
    if amount > balance:
        return await ctx.send("❌ Not enough balance.")

    if amount and choice:
        if choice.lower() not in options:
            await ctx.send(
                "Select a valid option: \n *red*, *black*, *green*, \n *1st*, *2nd*, *3rd*, \n *half1*, *half2*, \n *orphans*, *gserie*, *5/8*, *zerozone*, \n *numbers*"
            )
            return
        elif choice != "numbers":
            result = random.randint(0, 36)
            updateUser(ctx.author.id, balance - amount)
            newBalance = getUser(ctx.author.id)["balance"]

            win = getWin(result, choice)

            mult = getMultiplier(win, choice)
            assert mult is not None
            amount = int(amount * mult)
            updateUser(ctx.author.id, newBalance + amount)
            if "red" in numbas[str(result)]:
                decor = "🔴"
            elif "black" in numbas[str(result)]:
                decor = "⚫"
            else:
                decor = "🟢"
            if win:
                await ctx.send(
                    f"Number chosen was {result} {decor}, you won {amount} bolivares"
                )
            else:
                await ctx.send(
                    f"Number chosen was {result} {decor}, better luck next time"
                )
        else:
            if not numbers:
                return await ctx.send(
                    "You must provide numbers to bet on when choosing 'numeros'"
                )
            try:
                chosen_numbers = [
                    int(num) for num in numbers.split(" ") if 0 <= int(num) <= 36
                ]
                if not chosen_numbers:
                    return await ctx.send(
                        "You must provide valid numbers between 0 and 36"
                    )
            except ValueError:
                return await ctx.send(
                    "Please provide numbers only, separated by spaces"
                )

            result = random.randint(0, 36)
            updateUser(ctx.author.id, balance - amount)
            newBalance = getUser(ctx.author.id)["balance"]
            if "red" in numbas[str(result)]:
                decor = "🔴"
            elif "black" in numbas[str(result)]:
                decor = "⚫"
            else:
                decor = "🟢"

            if result in chosen_numbers:
                mult = 36 / len(chosen_numbers)
                amount = round(amount * mult)
                updateUser(ctx.author.id, newBalance + amount)
                await ctx.send(
                    f"Number chosen was {result}{decor}, you won {amount} bolivares"
                )
            else:
                await ctx.send(
                    f"Number chosen was {result}{decor}, better luck next time"
                )


@bot.command(help="Let's play rock, paper, scissors")
async def ppt(ctx, amount: str):

    bet_amount = 0
    balance = getUser(ctx.author.id)["balance"]
    balance = str(balance)
    if isinstance(amount, str) and amount.lower() == "allin":
        bet_amount = int(balance)
    else:
        try:
            bet_amount = int(amount)
            if bet_amount < 1:
                return await ctx.send("❌ You must bet at least 1 point.")
        except ValueError:
            return await ctx.send("❌ You must enter a number or 'allin'.")
    if bet_amount > int(balance):
        return await ctx.send("❌ Not enough balance.")
    newBalance = int(balance) - bet_amount
    updateUser(ctx.author.id, newBalance)

    embed = discord.Embed(
        title="Rock, Paper, Scissors",
        description="Click to start🤯",
        color=discord.Color.blue(),
    )
    view = PPTView(ctx.author.id, bet_amount)
    embed.set_thumbnail(url="attachment://Duala_dealer.webp")
    file = discord.File("assets/Duala_dealer.webp", filename="Duala_dealer.webp")
    await ctx.send(embed=embed, view=view, file=file)


@bot.command(help="Do you wanna test your luck with a lootbox ?")
async def lootbox(ctx):

    userID = ctx.author.id
    balance = getUser(userID)["balance"]
    if balance < 10000:
        return await ctx.send("Lootboxes cost 10.000 bolivares, try again later❌")
    else:
        newBalance = balance - 10000
        updateUser(userID, newBalance)
    rarity = openLootBox()
    cuantReward = handleLootBox(rarity=rarity, userID=userID)
    return await ctx.send(
        f"You got a **{rarity}** lootbox, you obtained {cuantReward} bolivares 🐱‍👤"
    )


@bot.command(help="Grab a reward if you're quick enough")
async def mine(ctx):
    global mio_activo, mio_reclamado

    if not mio_activo:
        await ctx.send("❌ No free bolivares now.")
        return

    if mio_reclamado:
        await ctx.send("⚠️ Reward already claimed.")
        return

    cantidad_de_bolívares_gratis = random.randint(2000, 7069)
    userBalance = getUser(ctx.author.id)["balance"]
    new_balance = userBalance + cantidad_de_bolívares_gratis
    updateUser(ctx.author.id, new_balance)

    mio_reclamado = True
    mio_activo = False

    await ctx.send(
        f"🏆 {ctx.author.mention} won {cantidad_de_bolívares_gratis} bolivares."
    )


@bot.command(help="Secret role for 200k")
async def buyRole(ctx):
    grupo = ctx.guild
    userID = ctx.author.id
    miembro = grupo.get_member(userID)

    roleID = 1463967996186726481
    rol = grupo.get_role(roleID)

    if rol is None:
        print("No role found")
    if miembro is None:
        print("Member not found")

    balance = getUser(userID)["balance"]

    if balance < 200000:
        return await ctx.send(
            "In order to buy this secret role, you gotta have 200.000 bolivares"
        )
    else:
        updateUser(userID, balance - 200000)
        await ctx.send("Purchasing secret role...")
        assert miembro is not None
        await miembro.add_roles(rol)
        print("Success with assinging role")
        return


@bot.command(help="Get one of many characters to sell or fight with them")
async def pull(ctx, quantity: int | None = None):
    userID = ctx.author.id
    balance = int(getUser(userID)["balance"])
    PULL_PRICE = 3000
    char = None

    if balance < PULL_PRICE:
        return await ctx.send("To pull a character, you need 3000 bolivares")

    print(f"Haciendo pull para {ctx.author.display_name}...")
    if quantity == None:
        balance -= PULL_PRICE
        updateUser(userID, balance)

        char = pullChar(userID)
        if char.level > 1:
            mensaje = f"♻️ **Repeated!** You already had a **{char.name}**. It leveled up to **{char.level}**! ⬆️"
        else:
            mensaje = (
                f"✨ **Congrats!** You got a new **{char.name}** ({char.rarity}) 🙀"
            )

        await ctx.send(mensaje)

    elif quantity > 1:
        if balance < PULL_PRICE * quantity:
            return await ctx.send(
                f"You need {PULL_PRICE * quantity} bolivares to pull {quantity} characters"
            )

        balance -= PULL_PRICE * quantity
        updateUser(userID, balance)

        nuevos = []
        repes = []

        for _ in range(quantity):
            char = pullChar(userID)
            if char.level > 1:
                repes.append(f"{char.name} ({char.rarity})")
            else:
                nuevos.append(f"{char.name} ({char.rarity})")

        # Construimos el mensaje final dinámicamente
        final_mensaje = "You got the following characters:\n"

        if nuevos:  # Si la lista tiene elementos, los unimos con comas
            final_mensaje += f"**NEW:** {', '.join(nuevos)}\n"
        if repes:
            final_mensaje += f"**Repeated:** {', '.join(repes)}\n"

        await ctx.send(final_mensaje)

    else:
        return await ctx.send("Quantity must be at least 1.")

    assert char is not None
    embed = char.toEmbed()
    archivo = discord.File(char.image, filename="char.webp")

    embed.set_image(url="attachment://char.webp")
    return await ctx.send(file=archivo, embed=embed)


@bot.command(help="Shows your inventory of companions")
async def inventory(ctx):
    userID = ctx.author.id
    inventory = getInventory(userID)

    if not inventory:
        return await ctx.send("No inventory to show")
    view = InventoryView(inventory)
    embed, file = view.get_embed()
    return await ctx.send(embed=embed, file=file, view=view)


@bot.command(help="Sell one or more companions for bolivares")
async def sell(ctx, *, option: str | None = None):
    if not option:
        return await ctx.send("You have to choose at least one slot in your inventory.")
    try:
        positions = {int(num) for num in option.split()}
    except ValueError:
        return await ctx.send(
            "Error: Enter numbers separated by spaces. Example: *sell 1 2 3"
        )

    userID = ctx.author.id
    inventory = getInventory(userID)

    if not inventory:
        return await ctx.send("Your inventory is empty.")
    if any(pos < 1 or pos > len(inventory) for pos in positions):
        return await ctx.send(
            f"Invalid position. Choose between 1 and {len(inventory)}."
        )

    selected = [inventory[pos - 1] for pos in sorted(positions)]
    total_reward = sum(char.getSellValue() for char in selected)

    for pos in sorted(positions, reverse=True):
        inventory.pop(pos - 1)

    balance = int(getUser(userID)["balance"])
    new_balance = balance + total_reward
    saveInventory(userID, inventory)
    updateUser(userID, new_balance)
    names = ", ".join(char.name for char in selected)

    return await ctx.send(
        f"You sold **{names}** for **{total_reward} bolivares**. "
        f"Your new balance is **{new_balance}**."
    )


@bot.command(help="Set a defender in case someone wants to fight you")
async def setDefender(ctx, option: int | None = None):

    if option == None:
        return await ctx.send(
            "If you wanna set a defender up you have to type *setDefender <position in your inventory>"
        )

    userID = ctx.author.id
    inventory = getInventory(userID)

    if int(option) <= 0 or int(option) > len(inventory):
        return await ctx.send("You have to select a valid position")

    charDef = inventory[option - 1]
    aux = inventory[0]
    inventory[0] = charDef
    inventory[option - 1] = aux

    saveInventory(userID, inventory)

    return await ctx.send(f"Your defender is now {charDef.name}")


@bot.command(help="Train a companion of your choice, with a cooldown obviously")
@commands.cooldown(1, 3600, commands.BucketType.user)
async def train(ctx, option: int | None = None):
    userID = ctx.author.id
    inventory = getInventory(userID)

    RANGOS_ENTRENAMIENTO = {
        "Common": (7, 13),
        "Uncommon": (3, 7),
        "Rare": (1, 3),
        "Epic": (0, 2),
    }

    if option == None:
        return await ctx.send(
            "Run the command like this: *train <postion in your inventory>"
        )

    if int(option) <= 0 or int(option) > len(inventory):
        ctx.command.reset_cooldown(ctx)
        return await ctx.send("You have to select a valid position")

    char = inventory[option - 1]

    if char.rarity not in RANGOS_ENTRENAMIENTO:
        ctx.command.reset_cooldown(ctx)
        return await ctx.send(
            f"Characters of rarity **{char.rarity}** cannot be trained."
        )

    min_lvl, max_lvl = RANGOS_ENTRENAMIENTO[char.rarity]
    levels_gained = random.randint(min_lvl, max_lvl)

    for _ in range(levels_gained):
        lvlUP(char)

    inventory[option - 1] = char
    saveInventory(userID, inventory)

    palabra_veces = "time" if levels_gained == 1 else "times"
    return await ctx.send(
        f"Your **{char.name}** leveled up {levels_gained} {palabra_veces}!"
    )


@bot.command(help="Fight your friend's defender")  # En el futuro meterle apuestas
async def combat(ctx, option: int | None = None, rival: discord.Member | None = None):
    if not option:
        return await ctx.send(
            "You have to choose who you are using in your fight, type *fight <fighter (inventory position)> <rival>"
        )
    if not rival:
        return await ctx.send(
            "No rival chosen, type *fight <fighter (inventory position)> <rival>"
        )

    userID = ctx.author.id
    userInventory = getInventory(userID)
    rivalInventory = getInventory(rival.id)

    if userInventory == []:
        return await ctx.send("You don't even have someone to fight with...")

    if rivalInventory == []:
        return await ctx.send("Your opponent hasn't even someone to defend them...")

    if len(userInventory) < option - 1:
        return await ctx.send("You don't even have that many characters...")

    userChar = userInventory[option - 1]
    rivalChar = rivalInventory[0]

    resumen, winner = fight(userChar, rivalChar)
    if len(resumen) > 1990:
        await ctx.send(resumen[:1990] + "...")
        await ctx.send("..." + resumen[1990:])
    else:
        await ctx.send(resumen)
    return


@bot.command(help="Fight some bosses or something")
async def boss(
    ctx, option: str | None = None, boss: int | None = None, char: int | None = None
):

    if not option:
        return await ctx.send(
            "Didn't choose an option, either type *boss list or fight <option>"
        )
    if option == "list":
        view = BossListView(bosses)
        embed, file = view.get_embed()
        return await ctx.send(embed=embed, file=file, view=view)
    elif option == "fight":
        if boss == None or char == None:
            return await ctx.send(
                "❌ You need to specify the Boss and your Character. Example: `*boss fight 1 3`"
            )

        if boss <= 0 or boss > len(bosses):
            return await ctx.send("❌ That Boss ID doesn't exist.")
        userID = ctx.author.id
        inventory = getInventory(userID)

        charPlayer = inventory[char - 1]

        resumen, winner = bossHandler(charPlayer, boss)

        if len(resumen) > 1990:
            await ctx.send(resumen[:1990] + "...")
            await ctx.send("..." + resumen[1990:])
        else:
            await ctx.send(resumen)
        return


@bot.command(help="Make Skylbot forget what you told it")
async def clear(ctx):
    user_name = ctx.author.display_name
    history.clear(user_name)
    await ctx.send("All done !")


@bot.command(help="Ask Skylbot about anything, it will answer")
async def ai(ctx, *, mensaje: str):
    try:
        await ctx.typing()
        user_name = ctx.author.display_name

        # 1. Obtener historial (operación en memoria rápida, segura por sus propios cerrojos)
        local_history_raw = history.getHistory(user_name)

        # 2. Construir la lista de mensajes de forma nativa para la API
        messages_payload = [{"role": "system", "content": prompt_inicial}]

        if local_history_raw:
            for block in local_history_raw:
                messages_payload.append({"role": "user", "content": block.question})
                messages_payload.append({"role": "assistant", "content": block.answer})

        # 3. Añadir el mensaje actual
        messages_payload.append(
            {"role": "user", "content": f"User name: {user_name}\n{mensaje}"}
        )

        # 4. Llamada a la API SIN el ai_lock global para permitir peticiones concurrentes
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat.completions.create,
                    model=model,
                    messages=messages_payload,
                    temperature=0.6,
                ),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            await ctx.send("⏳ La IA tardó demasiado. Intenta de nuevo más tarde.")
            return

        text = response.choices[0].message.content
        if not text:
            await ctx.send("⚠️ La IA devolvió una respuesta vacía.")
            return

        # 5. Guardar en el historial
        if isinstance(text, str):
            history.interact(user_name, TextBlock(mensaje, text))

        # 6. Enviar a Discord manejando el límite de 2000 caracteres
        for start in range(0, len(text), 2000):
            await ctx.send(text[start : start + 2000])

    except Exception as e:
        await ctx.send("⚠️ Error al conectar con GLM.")
        print("AI error:", repr(e))


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
