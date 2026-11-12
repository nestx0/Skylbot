import discord
from discord.ext import commands

from command_utils import parse_amount, parse_positions
from database.dataBase import getUser, updateUser

from .gacha import *


async def pull(ctx, quantity: str | None = None):
    userID = ctx.author.id
    balance = int(getUser(userID)["balance"])
    PULL_PRICE = 3000
    char = None

    if quantity is None:
        count = 1
    else:
        try:
            count = parse_amount(quantity, balance // PULL_PRICE)
        except ValueError as exc:
            return await ctx.send(str(exc))

    if count < 1:
        return await ctx.send("Quantity must be at least 1.")
    if balance < PULL_PRICE * count:
        return await ctx.send(
            f"You need {PULL_PRICE * count} bolivares to pull {count} characters"
        )

    print(f"Haciendo pull para {ctx.author.display_name}...")
    balance -= PULL_PRICE * count
    updateUser(userID, balance)

    if count == 1:
        char = pullChar(userID)
        if char.level > 1:
            mensaje = f"♻️ **Repeated!** You already had a **{char.name}**. It leveled up to **{char.level}**! ⬆️"
        else:
            mensaje = f"✨ **Congrats!** You got a new **{char.name}** ({char.rarity}) 🙀"
        await ctx.send(mensaje)

        embed = char.toEmbed()
        archivo = discord.File(char.image, filename="char.webp")
        embed.set_image(url="attachment://char.webp")
        return await ctx.send(file=archivo, embed=embed)

    nuevos = []
    repes = {}
    for _ in range(count):
        char = pullChar(userID)
        char_format = f"{char.name} ({char.rarity})"
        if char.level > 1:
            repes[char_format] = repes.get(char_format, 0) + 1
        else:
            nuevos.append(char_format)

    # Split long summaries into multiple messages instead of limiting pull quantity.
    message = f"You pulled {count} characters:\n"
    for heading, entries in (
        ("NEW", nuevos),
        ("Repeated", [f"{name} x{times}" for name, times in repes.items()]),
    ):
        if not entries:
            continue
        prefix = f"**{heading}:** "
        if len(message) + len(prefix) > 1900:
            await ctx.send(message)
            message = ""
        message += prefix
        for index, item in enumerate(entries):
            segment = (", " if index else "") + item
            if len(message) + len(segment) > 1900:
                await ctx.send(message)
                message = f"**{heading} (cont.):** {item}"
            else:
                message += segment
        message += "\n"
    return await ctx.send(message)


async def sell(ctx, *, option: str | None = None):
    if not option:
        return await ctx.send("You have to choose at least one slot in your inventory.")

    userID = ctx.author.id
    inventory = getInventory(userID)
    if not inventory:
        return await ctx.send("Your inventory is empty.")
    try:
        positions, _ = parse_positions(option, len(inventory))
    except ValueError as exc:
        return await ctx.send(str(exc))

    selected = [inventory[pos - 1] for pos in positions]
    total_reward = sum(char.getSellValue() for char in selected)

    for pos in reversed(positions):
        inventory.pop(pos - 1)

    balance = int(getUser(userID)["balance"])
    new_balance = balance + total_reward
    saveInventory(userID, inventory)
    updateUser(userID, new_balance)
    names = ", ".join(char.name for char in selected)
    msg = (
        f"You sold **{names}** for **{total_reward} bolivares**. "
        f"Your new balance is **{new_balance}**."
    )
    if len(msg) > 1900:
        msg = (f"You sold **{len(selected)}** characters for **{total_reward} bolivares**. "
               f"Your new balance is **{new_balance}**.")
    return await ctx.send(msg)


@commands.cooldown(1, 3600, commands.BucketType.user)
async def train(ctx, option: int | None = None):
    userID = ctx.author.id
    inventory = getInventory(userID)

    if option == None:
        ctx.command.reset_cooldown(ctx)
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
