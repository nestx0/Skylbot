### Opciones de contenido para tus Loot Boxes

#Monedas y fichas
#Boosters temporales
#Steal Token
#Rol

#Precio comun: 10k


import discord
import random
import dataBase
from shop.rewards import *

def openLootBox():
    resultado = random.randint(0,100)
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

    

#def handleLootBox(rarity: str, userID):

