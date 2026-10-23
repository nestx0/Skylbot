import discord

from discord.ext import commands
from database.dataBase import getUser, updateUser
from .gacha import *

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


@commands.cooldown(1, 3600, commands.BucketType.user)
async def train(ctx, option: int | None = None):
    userID = ctx.author.id
    inventory = getInventory(userID)

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