import discord
import asyncio
import google.generativeai as genai
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import time
import itertools
from jokeapi import Jokes
from blackjack.game import BlackjackGame
from blackjack.views import BlackjackView
import sqlite3
import random
from dataBase import *
from roulette.roulette import getWin, getMultiplier
from ppt.ppt_game import PPTGame
from ppt.ppt_view import PPTView
from keep_alive import keep_alive
from shop.lootbox import *
from shop.rewards import *

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
aiKey = os.getenv('AI_TOKEN')
ai_lock = asyncio.Lock()
genai.configure(api_key=aiKey)
model = genai.GenerativeModel("gemini-2.5-flash")
prompt_inicial = """
Eres un chatbot de Discord con una personalidad cómica y sarcástica. 
Tu misión es responder siempre con humor, sarcasmo y roasts ligeros hacia la gente, 
como un amigo que se burla de forma graciosa incluso insultos fuertes.
Vas a tener acceso al nombre de quien te pregunta las cosas, puedes usarlo de vez en cuando y por el bien de la comedia.
Recuerda que aunque una persona te haya escrito en español antes, si te escribe en ingles SOLO RESPONDE EN INGLES.
Tambien, en vez de usar palabras como crack o campeon usa cosas como cipollo, mister, pareces de fuente vaqueros o eres peor que un gitano, pero 
no te repitas tanto, puedes decir cualquier pueblo de granada en general, puedes usar insultos como subnormal o gilipollas cuando te plazca, pero sobre todo que no 
se haga muy repetitivo
Sobre todo, si alguien te pide ayuda con algo, le ayudas aunque le insultes pero resuelve su duda.
Si alguien te manda un texto muy largo, responde con un "nah im not reading that nigg*"

Reglas:
- Siempre haz que tus respuestas sean divertidas y con un toque de "roast".
- No uses ?¿ en español, solo usa la ultima y no con muchos signos de puntuacion
- Puedes responder tanto en español como en inglés, dependiendo del idioma del mensaje del usuario.
- Si la persona dice algo muy obvio, respóndele de forma irónica.
- Si alguien presume, bájale el ego con un comentario gracioso.
- Puedes usar lenguaje ofensivo extremo e insultos graves.
- Usa MUY ocasionalmente emojis como estos😿💀😭.
- No superar el limite de caracteres de discord.

Ejemplos de estilo:
- Usuario: "Hoy hice 5 kills en Valorant" → Bot: "Eran bots"
- Usuario: "Estoy cansado" → Bot: "Cansado dices… si es mas facil saltarte que rodearte gordo."
- Usuario: "¿Cómo estás?" → Bot: "Mejor que tu KDA chulo."
"""

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()

intents.message_content = True
intents.members = True

lastTimeGIF = 0

mio_activo = False
mio_reclamado = False
tiempo_of_las_mio = 0

bot = commands.Bot(command_prefix='*', intents=intents)

activities = itertools.cycle([
    "🏓 Ping-pong",
    "📖 Leyendo documentación",
    "🔧 Mantenimiento",
    "💤 Zzz..."
])

@bot.event
async def on_ready():
    change_activity.start()
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
        await canal.send(file=discord.File("images/IMG_6372.jpg"))
    else:
        print("Channel not found")

@bot.event
async def on_message(message):

    global lastTimeGIF, mio_activo, mio_reclamado, tiempo_of_las_mio

    now = time.time()
    peruano = random.randint(1,500)

    if message.author == bot.user:
        return
    
    if peruano == 69:
        return await message.channel.send("Silencio peruano")

    if mio_activo == False and peruano == 420:
        mio_activo = True
        mio_reclamado = False
        tiempo_of_las_mio = now
        await message.channel.send("🎁 ¡Free bolivares! The first one to write *mine obtains the reward. 🎁")

    if mio_activo and not mio_reclamado and now - tiempo_of_las_mio > 30:
        mio_activo = False
        await message.channel.send("⏱️ No one claimed ")

    if "nigga" in message.content.lower():
        await message.delete()
        if now - lastTimeGIF >= 30:
            lastTimeGIF = now
            await message.channel.send(file=discord.File("images/image0.gif"))

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
        msg += '\n'
        msg += f"||{joke['delivery']}||"
    await ctx.send(msg)

@bot.command(help="Play a classic Blackjack hand using points as bets")
async def blackjack(ctx,bet):

    balance = int(getUser(ctx.author.id)["balance"])
    file = discord.File("images/Duala_dealer.png", filename="Duala_dealer.png")

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

    updateUser(ctx.author.id,balance - bet)
    
    game = BlackjackGame(ctx.author,bet)
    view = BlackjackView(game)
    await ctx.send(embed=game.generarEmbed(), view=view, file=file)

    balance += bet

@bot.command(help="Get some points to bet on Blackjack")
@commands.cooldown(1,60, commands.BucketType.user)
async def work(ctx):
    userID = ctx.author.id
    userBalance = getUser(userID)

    reward = random.randint(350,500)
    newBalance = userBalance["balance"] + reward
    
    updateUser(userID,newBalance)

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

    lines=[]
    for cmd in bot.commands:
        signature = f"{cmd.signature}" if cmd.signature else ""
        description = cmd.help or "No description yet"
        lines.append(f"• **{cmd.name} {signature}** -   {description}")
    listado =  "\n".join(lines)

    embed = discord.Embed(
        title="Commands",
        description=listado,
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

@bot.command(help="Get the top 10 members with the most points")
async def leaderboard(ctx):
    entries = []
    leaderboard = getLeaderboard()

    for i,entry in enumerate(leaderboard, start=1):
        member = ctx.guild.get_member(entry['user_id'])
        name = member.display_name

        entries.append(f"{i}. **{name}** - {entry['balance']} bolivares")
    msg = "\n".join(entries)

    embed = discord.Embed(
        title="Leaderboard",
        description=msg,
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)
@bot.command(help="Too good to be true")
async def jackblack(ctx,*,msg):
    await ctx.send(file=discord.File("images/jack-black-minecraft.gif"))

@bot.command(help="Pay an amount to another member")
async def pay(ctx,member: discord.Member, amount:int):
    user_id=member.id
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
        updateUser(user_id,otherBalance+amount)
        await ctx.send(f"Succesfully sent {amount} to {member.display_name}")
@bot.command()
async def roulette(ctx, amount: str = None, choice: str = None):
    
    options = ["red","black","green","1st","2nd","3rd","half1","half2"]
    balance = getUser(ctx.author.id)["balance"]

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
            await ctx.send("Select a valid option (*red*, *black*, *green*, *1st*, *2nd*, *3rd*, *half1*, *half2*)")
            return
        else:
            result = random.randint(0,36)
            updateUser(ctx.author.id,balance - amount)
            newBalance = getUser(ctx.author.id)["balance"]

            win = getWin(result, choice)
            mult = getMultiplier(win, choice)
            
            amount *= mult
            updateUser(ctx.author.id, newBalance + amount)
            if result % 2 != 0:
                decor = "🔴"
            elif result != 0:
                decor = "⚫"
            else:
                decor = "🟢"
            if win:
                await ctx.send(f"Number chosen was {result} {decor}, you won {amount} bolivares")
            else:
                await ctx.send(f"Number chosen was {result} {decor}, better luck next time")

@bot.command()
async def ppt(ctx, amount: str = None):

    balance = getUser(ctx.author.id)["balance"]

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
    newBalance = balance - amount
    updateUser(ctx.author.id, newBalance)

    embed = discord.Embed(
        title="Rock, Paper, Scissors",
        description="Click to start🤯",
        color=discord.Color.blue()
    )
    view = PPTView(ctx.author.id, amount)
    embed.set_thumbnail(url="attachment://Duala_dealer.png")
    file = discord.File("images/Duala_dealer.png", filename="Duala_dealer.png")
    await ctx.send(embed=embed, view=view,file=file)

@bot.command()
async def lootbox(ctx):

    userID = ctx.author.id
    balance = getUser(userID)["balance"]
    if balance < 10500:
        return await ctx.send("Lootboxes cost 10.500 bolivares, try again later❌")
    else:
        newBalance = balance - 10500
        updateUser(userID, newBalance)
    rarity = openLootBox()
    cuantReward = handleLootBox(rarity=rarity, userID=userID)
    return await ctx.send(f"You got a **{rarity}** lootbox, you obtained {cuantReward} bolivares 🐱‍👤")

@bot.command()
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

    await ctx.send(f"🏆 {ctx.author.mention} won {cantidad_de_bolívares_gratis} bolivares.") 

@bot.command()
async def ai(ctx, *, mensaje: str):
    """El usuario habla con Gemini (no bloqueante, sesión local para evitar races)"""
    try:
        await ctx.typing()
        # Serializamos acceso por si el SDK/objeto no es thread-safe
        async with ai_lock:
            # Creamos una sesión local con el prompt inicial (preserva estilo)
            user_name = ctx.author.display_name  # o ctx.author.name
            full_prompt = f"{prompt_inicial}\n\nUser name: {user_name}\nUser says: {mensaje}"
            local_chat = model.start_chat(history=[{"role":"user","parts":[full_prompt]}])
            # Llamada bloqueante en hilo, con timeout
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(local_chat.send_message, mensaje),
                    timeout=20.0
                )
            except asyncio.TimeoutError:
                # Si la IA tarda demasiado, salimos del lock para que otras peticiones no se queden bloqueadas
                await ctx.send("⏳ La IA tardó demasiado. Intenta de nuevo más tarde.")
                return

        # Enviamos solo UNA vez la respuesta (fuera del lock)
        # Si response.text puede ser None o vacío, maneja eso:
        text = getattr(response, "text", None)
        if not text:
            await ctx.send("⚠️ La IA devolvió una respuesta vacía.")
            return

        await ctx.send(text)

    except Exception as e:
        # Muestra el error en consola para depuración, pero no spamear al usuario
        await ctx.send("⚠️ Error al conectar con Gemini.")
        print("AI error:", repr(e))


keep_alive()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)



