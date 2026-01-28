import json
import random

import discord
from discord.ui import Button, View

from dataBase import *

stats = ["ATK", "DEF", "SPE", "LCK", "HP"]

personajesComun = [
    {
        "id": 1,
        "name": "Apple Cat",
        "desc": "Just chilling, he likes apples",
        "rarity": "Common",
        "stats": {"HP": 10, "ATK": 2, "DEF": 3, "SPE": 1, "LCK": 4},
        "lvl": 1,
        "image": "images/characters/apple_cat.jpeg",
    },
    {
        "id": 2,
        "name": "Angy Cat",
        "desc": "No one knows what's inside his little brain",
        "rarity": "Common",
        "stats": {"HP": 8, "ATK": 4, "DEF": 2, "SPE": 2, "LCK": 2},
        "lvl": 1,
        "image": "images/characters/hmm_cat.jpeg",
    },
    {
        "id": 3,
        "name": "Confused Cat",
        "desc": "He got in that state after his first computer science class",
        "rarity": "Common",
        "stats": {"HP": 9, "ATK": 1, "DEF": 4, "SPE": 3, "LCK": 2},
        "lvl": 1,
        "image": "images/characters/huh_cat.jpeg",
    },
    {
        "id": 4,
        "name": "1000 Yards Cat",
        "desc": "The look in his eyes comes from the destruction of Palestine",
        "rarity": "Common",
        "stats": {"HP": 11, "ATK": 2, "DEF": 3, "SPE": 4, "LCK": 1},
        "lvl": 1,
        "image": "images/characters/nuke_cat.jpeg",
    },
]
personajesUncommon = [
    {
        "id": 5,
        "name": "Balls Cat",
        "desc": "He thinks you have nice balls, doesn't matter what your gender is",
        "rarity": "Uncommon",
        "stats": {"HP": 15, "ATK": 4, "DEF": 6, "SPE": 1, "LCK": 4},
        "lvl": 1,
        "image": "images/characters/nice_cat.jpeg",
    },
    {
        "id": 6,
        "name": "Maxwell",
        "desc": "Please do not bend",
        "rarity": "Uncommon",
        "stats": {"HP": 14, "ATK": 3, "DEF": 7, "SPE": 2, "LCK": 1},
        "lvl": 1,
        "image": "images/characters/maxwell_cat.jpeg",
    },
    {
        "id": 7,
        "name": "Eyebrow Cat",
        "desc": "He doesn't agree on your political beliefs",
        "rarity": "Uncommon",
        "stats": {"HP": 15, "ATK": 7, "DEF": 4, "SPE": 2, "LCK": 2},
        "lvl": 1,
        "image": "images/characters/eyebrow_cat.jpeg",
    },
    {
        "id": 8,
        "name": "Bleh Cat",
        "desc": "Just a Silly Billy",
        "rarity": "Uncommon",
        "stats": {"HP": 16, "ATK": 2, "DEF": 6, "SPE": 4, "LCK": 3},
        "lvl": 1,
        "image": "images/characters/bleh_cat.jpeg",
    },
]
personajesRaro = [
    {
        "id": 9,
        "name": "Suspicious Cat",
        "desc": "He is sceptical about everything in this world",
        "rarity": "Rare",
        "stats": {"HP": 20, "ATK": 10, "DEF": 6, "SPE": 7, "LCK": 3},
        "lvl": 1,
        "image": "images/characters/sus_cat.jpeg",
    },
    {
        "id": 10,
        "name": "Surprised Cat",
        "desc": "This was his reaction when he saw 9/11, hasn't changed since then",
        "rarity": "Rare",
        "stats": {"HP": 22, "ATK": 7, "DEF": 7, "SPE": 7, "LCK": 4},
        "lvl": 1,
        "image": "images/characters/surprised_cat.jpeg",
    },
    {
        "id": 11,
        "name": "Microbio Cat",
        "desc": "So small he doesn't have mass",
        "rarity": "Rare",
        "stats": {"HP": 24, "ATK": 7, "DEF": 12, "SPE": 5, "LCK": 3},
        "lvl": 1,
        "image": "images/characters/micro_cat.jpeg",
    },
    {
        "id": 12,
        "name": "Beluga Cat",
        "desc": "Lord of Discord",
        "rarity": "Rare",
        "stats": {"HP": 22, "ATK": 5, "DEF": 6, "SPE": 4, "LCK": 11},
        "lvl": 1,
        "image": "images/characters/beluga_cat.jpeg",
    },
]


def pullChar(userID):
    print("Pulling")
    rarity = random.randint(0, 100)
    inventory = getInventory(userID)
    print("Got inv")

    if rarity >= 0 and rarity <= 60:
        char = Character(random.choice(personajesComun))
    elif rarity > 60 and rarity <= 90:
        char = Character(random.choice(personajesUncommon))
    elif rarity > 90 and rarity <= 100:
        char = Character(random.choice(personajesRaro))

    encontrado = False
    if inventory:
        for i, item in enumerate(inventory):
            if item.id == char.id:
                print("Leveling up")
                inventory[i] = lvlUP(inventory[i])
                print("Finish leveling up")
                encontrado = True
                char = inventory[i]
                break
        if not encontrado:
            inventory.append(char)
    else:
        inventory.append(char)
    print("Finish logic")
    saveInventory(userID, inventory)
    print("Saved")
    print(inventory)

    return char


class Character:
    def __init__(self, info: dict):
        self.id = info.get("id")
        self.name = info.get("name", "No name")
        self.desc = info.get("desc", "")
        self.rarity = info.get("rarity", "Unknown")
        self.level = info.get("lvl", 0)
        self.stats = info.get("stats", None)
        self.image = info.get("image", "images/characters/maxwell_cat.jpeg")
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


class InventoryView(View):
    def __init__(self, data):
        super().__init__(timeout=60)
        self.data = data
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.data) - 1

    def get_embed(self):
        character = self.data[self.current_page]
        file = discord.File(character.image, filename="char.jpeg")

        embed = discord.Embed(
            title=f"🎒 Inventario: {character.name}",
            description=character.desc,
            color=discord.Color.gold(),
        )

        for stat, valor in character.stats.items():
            embed.add_field(name=stat, value=str(valor), inline=True)
        embed.add_field(name="LVL", value=str(character.level))

        embed.set_image(url=f"attachment://char.jpeg")
        embed.set_footer(text=f"Página {self.current_page + 1} de {len(self.data)}")

        return embed, file

    @discord.ui.button(label="◀ Anterior", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.update_buttons()

        embed, file = self.get_embed()
        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )

    @discord.ui.button(label="Siguiente ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.update_buttons()
        embed, file = self.get_embed()
        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )


def lvlUP(char: Character):

    firstStat = random.choice(stats)
    secondStat = random.choice(stats)

    char.level += 1

    if char.rarity == "Common":
        char.stats[firstStat] += 2
        char.stats[secondStat] += 1
    elif char.rarity == "Uncommon":
        char.stats[firstStat] += 4
        char.stats[secondStat] += 2
    elif char.rarity == "Rare":
        char.stats[firstStat] += 6
        char.stats[secondStat] += 4

    return char


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
    if inventory:
        listCharacters = [char.toDICT() for char in inventory]
        charactersJSON = json.dumps(listCharacters)
        updateInventory(userID, charactersJSON)
