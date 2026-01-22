import random

import discord

personajesComun = [
    {"id": 1, "name": "Cat1", "desc": "generic cat 1", "rarity": "Common"},
    {"id": 2, "name": "Cat2", "desc": "generic cat 2", "rarity": "Common"},
    {"id": 3, "name": "Cat3", "desc": "generic cat 3", "rarity": "Common"},
    {"id": 4, "name": "Cat4", "desc": "generic cat 4", "rarity": "Common"},
]
personajesUncommon = [
    {"id": 5, "name": "Cat5", "desc": "generic cat 5", "rarity": "Uncommon"},
    {"id": 6, "name": "Cat6", "desc": "generic cat 6", "rarity": "Uncommon"},
    {"id": 7, "name": "Cat7", "desc": "generic cat 7", "rarity": "Uncommon"},
    {"id": 8, "name": "Cat8", "desc": "generic cat 8", "rarity": "Uncommon"},
]
personajesRaro = [
    {"id": 9, "name": "Cat9", "desc": "generic cat 9", "rarity": "Rare"},
    {"id": 10, "name": "Cat10", "desc": "generic cat 10", "rarity": "Rare"},
    {"id": 11, "name": "Cat11", "desc": "generic cat 11", "rarity": "Rare"},
    {"id": 12, "name": "Cat12", "desc": "generic cat 12", "rarity": "Rare"},
]


def pull():
    rarity = random.randint(0, 100)


class Character:
    def __init__(self, info: dict):
        self.id = info.get("id")
        self.name = info.get("name", "No name")
        self.desc = info.get("desc", "")
        self.rarity = info.get("rarity", "Unknown")
        if "image" in info:
            self.image = info.get("image")
        if self.rarity == "Common":
            self.color = discord.Color.dark_gray()
        elif self.rarity == "Uncommon":
            self.color = discord.Color.dark_green()
        elif self.rarity == "Rare":
            self.color = discord.Color.dark_orange()
        elif self.rarity == "Epic":
            self.color = discord.Color.dark_purple()
        else:
            self.color = discord.Color.dark_gold()

    def toEmbed(self):
        msg = self.name + "\n" + self.desc + "\n" + self.rarity
        return discord.Embed(title=self.name, description=msg, color=self.color)
