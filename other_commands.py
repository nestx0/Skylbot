import random
from typing import Any, cast

import discord
from discord.ext import commands
from jokeapi import Jokes

from command_utils import parse_amount
from database.dataBase import getLeaderboard, getUser, updateUser

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="*", intents=intents)
bot.help_command = commands.DefaultHelpCommand(
    sort_commands=True,
    command_attrs={
        "help": "Show the command list or detailed examples.\nUsage: *help [command]\nExamples: *help | *help pull | *help sellplant",
        "brief": "Show command syntax and examples",
    },
)

mio_estado = {"activo": False, "reclamado": False}


async def guide(ctx):

    lines = []
    for cmd in sorted(bot.commands, key=lambda cmd: cmd.name.lower()):
        signature = f" {cmd.signature}" if cmd.signature else ""
        description = cmd.short_doc or "No description yet"
        lines.append(f"• **{cmd.name}{signature}** - {description}")

    # Keep *guide concise; detailed examples are available via *help <command>.
    pages = []
    current = ""
    for line in lines:
        if current and len(current) + len(line) + 1 > 3900:
            pages.append(current)
            current = ""
        current += ("\n" if current else "") + line
    if current:
        pages.append(current)

    for index, page in enumerate(pages or ["No commands available."]):
        suffix = f" ({index + 1}/{len(pages)})" if len(pages) > 1 else ""
        embed = discord.Embed(
            title=f"Commands{suffix}", description=page, color=discord.Color.green()
        )
        await ctx.send(embed=embed)


async def ping(ctx):
    await ctx.send("**pong**")


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


async def joke(ctx):
    j = await Jokes()
    joke = cast(dict[str, Any], await j.get_joke())

    msg = ""

    if joke["type"] == "single":
        msg = joke["joke"]
    else:
        msg = joke["setup"]
        msg += "\n"
        msg += f"||{joke['delivery']}||"
    await ctx.send(msg)


@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    userID = ctx.author.id
    userBalance = getUser(userID)

    reward = random.randint(350, 500)
    newBalance = userBalance["balance"] + reward

    updateUser(userID, newBalance)

    await ctx.send(f"You've earned {reward}, your balance is {newBalance}")


async def pay(ctx, member: discord.Member, amount: str):
    user_id = member.id
    balance = getUser(ctx.author.id)["balance"]

    try:
        amount = parse_amount(amount, balance)
    except ValueError as exc:
        return await ctx.send(str(exc))

    if user_id == ctx.author.id or amount < 1:
        return await ctx.send("How are you supposed to do that")

    if balance < amount:
        return await ctx.send(f"You're poor, your maximum balance is {balance}")

    otherBalance = getUser(user_id)["balance"]
    updateUser(ctx.author.id, balance - amount)
    updateUser(user_id, otherBalance + amount)
    await ctx.send(f"Succesfully sent {amount} to {member.display_name}")


async def balance(ctx):
    balance = getUser(ctx.author.id)["balance"]
    mensaje = ""

    if balance == 0:
        mensaje = ", you're fucking broke"

    await ctx.send(f"Your current balance is {balance}{mensaje}")


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


async def mine(ctx):
    if not mio_estado["activo"]:
        await ctx.send("❌ No free bolivares now.")
        return

    if mio_estado["reclamado"]:
        await ctx.send("⚠️ Reward already claimed.")
        return

    cantidad_de_bolívares_gratis = random.randint(2000, 7069)
    userBalance = getUser(ctx.author.id)["balance"]
    new_balance = userBalance + cantidad_de_bolívares_gratis
    updateUser(ctx.author.id, new_balance)

    mio_estado["reclamado"] = True
    mio_estado["activo"] = False

    await ctx.send(
        f"🏆 {ctx.author.mention} won {cantidad_de_bolívares_gratis} bolivares."
    )
