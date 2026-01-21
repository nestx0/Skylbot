from cgitb import grey

import discord

personajes = [
    {"id": 1, "name": "Cat1", "desc": "generic cat 1", "rarity": "Common"},
    {"id": 2, "name": "Cat2", "desc": "generic cat 2", "rarity": "Uncommon"},
    {"id": 3, "name": "Cat3", "desc": "generic cat 3", "rarity": "Rare"},
    {"id": 4, "name": "Cat4", "desc": "generic cat 4", "rarity": "Epic"},
]


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
