import json
import random
from typing import ClassVar

import discord

from dataBase import *

from .personajesComun import personajesComun
from .personajesEpic import personajesEpico
from .personajesRaro import personajesRaro
from .personajesUncommon import personajesUncommon

stats = ["ATK", "DEF", "SPE", "LCK", "HP"]
MAX_LEVEL = 250


class RarityConfig:
    DATA: ClassVar[dict] = {
        "Common": {
            "color": discord.Color.dark_gray(),
            "sell_base": 500,
            "hp_gain": 3,
            "random_gains": [2, 1],
        },
        "Uncommon": {
            "color": discord.Color.dark_green(),
            "sell_base": 2000,
            "hp_gain": 6,
            "random_gains": [4, 2, 1],
        },
        "Rare": {
            "color": discord.Color.dark_orange(),
            "sell_base": 7000,
            "hp_gain": 10,
            "random_gains": [6, 4, 3, 2],
        },
        "Epic": {
            "color": discord.Color.dark_purple(),
            "sell_base": 15000,
            "hp_gain": 15,
            "random_gains": [10, 8, 5, 2],
        },
        "Legendary": {
            "color": discord.Color.dark_gold(),
            "sell_base": 30000,
            "hp_gain": 20,
            "random_gains": [15, 12, 8, 5],
        },
    }

    @classmethod
    def get(cls, rarity: str) -> dict:
        return cls.DATA.get(
            rarity,
            {
                "color": discord.Color.dark_gold(),
                "sell_base": 0,
                "hp_gain": 0,
                "random_gains": [],
            },
        )


def pullChar(userID):
    rarity = random.randint(0, 100)
    inventory = getInventory(userID)

    char = Character(random.choice(personajesComun))
    if rarity > 60 and rarity <= 85:
        char = Character(random.choice(personajesUncommon))
    elif rarity > 85 and rarity <= 95:
        char = Character(random.choice(personajesRaro))
    elif rarity > 95 and rarity <= 100:
        char = Character(random.choice(personajesEpico))

    encontrado = False
    if inventory:
        for i, item in enumerate(inventory):
            if item.id == char.id:
                inventory[i] = lvlUP(inventory[i])
                encontrado = True
                char = inventory[i]
                break
        if not encontrado:
            inventory.append(char)
    else:
        inventory.append(char)
    saveInventory(userID, inventory)

    return char


class Character:
    def __init__(self, info: dict):
        self.id = info.get("id")
        self.name = info.get("name", "No name")
        self.desc = info.get("desc", "")
        self.rarity = info.get("rarity", "Unknown")
        self.level = info.get("lvl", 0)
        self.stats = info.get("stats", None)
        imagen_guardada = info.get("image", "images/characters/maxwell_cat.webp")
        self.image = (
            imagen_guardada.replace(".jpeg", ".webp")
            .replace(".png", ".webp")
            .replace(".jpg", ".webp")
        )
        self.color = RarityConfig.get(self.rarity)["color"]

    def levelUP(self, times: int = 1):
        config = RarityConfig.get(self.rarity)
        for _ in range(times):
            if self.level >= MAX_LEVEL:
                break
            self.level += 1
            if self.stats:
                self.stats["HP"] += config["hp_gain"]
                for gain in config["random_gains"]:
                    stat_to_boost = random.choice(stats)
                    self.stats[stat_to_boost] += gain

        return self

    def toEmbed(self):
        msg = self.name + "\n" + self.desc + "\n" + self.rarity
        return discord.Embed(title=self.name, description=msg, color=self.color)

    def getSellValue(self) -> int:
        baseValue = RarityConfig.get(self.rarity)["sell_base"]
        finalValue = round(baseValue * self.level / 0.8)
        return finalValue

    def toDICT(self):
        data = {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "rarity": self.rarity,
            "lvl": self.level,
            "stats": self.stats,
            "image": self.image,
        }
        return data


def lvlUP(char: Character):
    return char.levelUP()


def getInventory(userID) -> list:
    data = getUser(userID)
    raw_inventory = data.get("inventory", [])

    if isinstance(raw_inventory, list):
        inventory_data = raw_inventory

    elif isinstance(raw_inventory, str):
        try:
            inventory_data = json.loads(raw_inventory)
        except json.JSONDecodeError:
            print("Error: El inventario en la DB no es un JSON válido.")
            inventory_data = []
    else:
        inventory_data = []

    if not inventory_data:
        return []

    return [Character(char) for char in inventory_data]


def saveInventory(userID, inventory: list):
    if inventory is not None:
        listCharacters = [char.toDICT() for char in inventory]
        charactersJSON = json.dumps(listCharacters)
        updateInventory(userID, charactersJSON)
