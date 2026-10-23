# Monedas y fichas
# Boosters temporales
# Steal Token
# Rol
# Precio comun: 10k

import random

from vicio.rewards import coinReward
from database.dataBase import getUser, updateUser


def openLootBox():
    resultado = random.randint(0, 100)
    if resultado >= 0 and resultado < 70:
        return "Common"
    elif resultado >= 70 and resultado < 90:
        return "Rare"
    elif resultado >= 90 and resultado < 99:
        return "Epic"
    else:
        return "Legendary"


def handleLootBox(rarity: str, userID):
    typeReward = coinReward(rarity)
    cuantReward = typeReward.applyReward(userID)
    return cuantReward


#====================================================================================================


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
        f"You got a **{rarity}** lootbox, you obtained {cuantReward} bolivares 🐱👤"
    )