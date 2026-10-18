import copy
import json
import random

import discord
from discord.ui import Button, View

from dataBase import *

from .bosses import bosses
from .personajesComun import personajesComun
from .personajesEpic import personajesEpico
from .personajesRaro import personajesRaro
from .personajesUncommon import personajesUncommon

stats = ["ATK", "DEF", "SPE", "LCK", "HP"]


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

    def getSellValue(self) -> int:
        rarity = self.rarity
        lvl = self.level

        baseValue = 0
        if rarity == "Common":
            baseValue = 500
        elif rarity == "Uncommon":
            baseValue = 2000
        elif rarity == "Rare":
            baseValue = 7000
        elif rarity == "Epic":
            baseValue = 15000
        elif rarity == "Legendary":
            baseValue = 30000

        finalValue = round(baseValue * lvl / 0.8)
        return finalValue


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
            title=f"🎒 Inventory: {character.name}",
            description=character.desc,
            color=discord.Color.gold(),
        )

        embed.add_field(name="Rarity", value=character.rarity)
        embed.add_field(name="Sell Value", value=str(character.getSellValue()))
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Invisible field

        for stat, valor in character.stats.items():
            embed.add_field(name=stat, value=str(valor), inline=True)
        embed.add_field(name="LVL", value=str(character.level))

        embed.set_image(url=f"attachment://char.jpeg")
        embed.set_footer(text=f"Page {self.current_page + 1} out of {len(self.data)}")

        return embed, file

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.update_buttons()

        embed, file = self.get_embed()
        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.update_buttons()
        embed, file = self.get_embed()
        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )


class BossListView(View):
    def __init__(self, data):
        super().__init__(timeout=60)
        self.data = [Character(boss_dict) for boss_dict in bosses]
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.data) - 1

    def get_embed(self):
        boss = self.data[self.current_page]
        file = discord.File(boss.image, filename="boss.jpeg")

        embed = discord.Embed(
            title=f"👹 Boss Arena: {boss.name}",
            description=boss.desc,
            color=discord.Color.dark_red(),
        )

        embed.add_field(name="Difficulty", value=boss.rarity)

        boss_id = self.current_page + 1
        embed.add_field(name="Boss ID", value=f"#{boss_id}")
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        if boss.stats is not None:
            for stat, valor in boss.stats.items():
                embed.add_field(name=stat, value=str(valor), inline=True)
        embed.add_field(name="LVL", value=str(boss.level))

        embed.set_image(url="attachment://boss.jpeg")

        embed.set_footer(
            text=f"Boss {boss_id} out of {len(self.data)} | Use *boss fight {boss_id} to challenge!"
        )

        return embed, file

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.update_buttons()
        embed, file = self.get_embed()
        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.update_buttons()
        embed, file = self.get_embed()
        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )


def lvlUP(char: Character):

    if char.level >= 250:  # Level cap de 250
        return char

    firstStat = random.choice(stats)
    secondStat = random.choice(stats)
    thirdStat = random.choice(stats)
    fourthStat = random.choice(stats)

    char.level += 1
    if char.stats is not None:
        if char.rarity == "Common":
            char.stats["HP"] += 3
            char.stats[firstStat] += 2
            char.stats[secondStat] += 1
        elif char.rarity == "Uncommon":
            char.stats["HP"] += 6
            char.stats[firstStat] += 4
            char.stats[secondStat] += 2
            char.stats[thirdStat] += 1
        elif char.rarity == "Rare":
            char.stats["HP"] += 10
            char.stats[firstStat] += 6
            char.stats[secondStat] += 4
            char.stats[thirdStat] += 3
            char.stats[fourthStat] += 2
        elif char.rarity == "Epic":
            char.stats["HP"] += 15
            char.stats[firstStat] += 10
            char.stats[secondStat] += 8
            char.stats[thirdStat] += 5
            char.stats[fourthStat] += 2

    return char


def fight(char1, char2):
    p1 = copy.deepcopy(char1)
    p2 = copy.deepcopy(char2)
    resumen = ""

    p1_max_hp = p1.stats["HP"]
    p2_max_hp = p2.stats["HP"]

    p1_init = p1.stats["SPE"] * random.uniform(0.9, 1.1)
    p2_init = p2.stats["SPE"] * random.uniform(0.9, 1.1)

    if p2_init > p1_init:
        attacker, defender = p2, p1
        atk_max_hp, def_max_hp = p2_max_hp, p1_max_hp
    else:
        attacker, defender = p1, p2
        atk_max_hp, def_max_hp = p1_max_hp, p2_max_hp

    resumen += f"⚔️ **{attacker.name}** vs **{defender.name}**!\n"
    resumen += f"💨 **{attacker.name}** is faster and takes the first strike.\n\n"

    turno = 1
    frenzy_multiplier = 1.0  # En lugar de *= 2, le sumaremos 0.3 cada turno

    while p1.stats["HP"] > 0 and p2.stats["HP"] > 0:
        if random.randint(1, 100) <= 5:
            if attacker.stats["LCK"] > defender.stats["LCK"]:
                heal = int(atk_max_hp * 0.15)
                attacker.stats["HP"] += heal
                resumen += f"🍀 **LUCKY DROP!** {attacker.name} found a health potion and recovered {heal} HP!\n"
            else:
                dmg = int(defender.stats["HP"] * 0.10)
                defender.stats["HP"] -= dmg
                resumen += f"⚡ **ARENA HAZARD!** A stray lightning hit {defender.name} for {dmg} damage!\n"

        dodge_chance = min(
            25.0,
            (defender.stats["SPE"] / attacker.stats["SPE"]) * 5
            + (defender.stats["LCK"] / 20),
        )

        if random.uniform(0, 100) < dodge_chance:
            resumen += (
                f"🛡️ **Turn {turno}:** {defender.name} gracefully dodged the attack!\n"
            )
        else:
            base_dmg = (100 * attacker.stats["ATK"]) / (100 + defender.stats["DEF"])
            varianza = random.uniform(0.85, 1.15)

            desperation_mult = 1.0
            is_desperate = False
            if attacker.stats["HP"] <= (atk_max_hp * 0.20):
                desperation_mult = 1.5
                is_desperate = True

            prob_critico = min(50.0, attacker.stats["LCK"] / 10.0)
            es_critico = random.uniform(0, 100) < prob_critico
            multiplicador_crit = 1.5 if es_critico else 1.0

            final_dmg = round(
                base_dmg
                * varianza
                * multiplicador_crit
                * desperation_mult
                * frenzy_multiplier
            )
            if final_dmg < 1:
                final_dmg = 1

            defender.stats["HP"] -= final_dmg
            if defender.stats["HP"] < 0:
                defender.stats["HP"] = 0

            crit_text = " **(CRITICAL HIT! 💥)**" if es_critico else ""
            desp_text = " **(DESPERATION STRIKE! 💢)**" if is_desperate else ""

            resumen += f"🥊 **Turn {turno}:** {attacker.name} deals {final_dmg} damage!{crit_text}{desp_text} ({defender.name} HP: {defender.stats['HP']})\n"

        if defender.stats["HP"] <= 0:
            resumen += f"\n🏆 **FIGHT OVER! {attacker.name} stands victorious!**"
            break

        attacker, defender = defender, attacker
        atk_max_hp, def_max_hp = def_max_hp, atk_max_hp
        turno += 1

        frenzy_multiplier += 0.3

        if turno == 10:
            resumen += "\n🔥 **SUDDEN DEATH! ALL DAMAGE IS MASSIVELY INCREASED!** 🔥\n"

        if turno > 20:
            resumen += "\n⏳ **Time Limit Reached! It's a DRAW!**"
            break

    return resumen, attacker.name


def bossHandler(charP, option: int):
    player = copy.deepcopy(charP)
    boss_raw = copy.deepcopy(bosses[option - 1])

    boss = Character(boss_raw)

    if boss.name == "Hacienda":
        player.stats["HP"] /= 2
        player.stats["ATK"] /= 2
        player.stats["DEF"] /= 2
        player.stats["SPE"] /= 2
        player.stats["LCK"] /= 2
    if boss.name == "Pringles Floppa":
        assert boss.stats is not None
        boss.stats["HP"] = round(player.stats["HP"] * 1.15)
        boss.stats["ATK"] = round(player.stats["ATK"] * 1.15)
        boss.stats["DEF"] = round(player.stats["DEF"] * 1.15)
        boss.stats["SPE"] = round(player.stats["SPE"] * 1.15)
        boss.stats["LCK"] = round(player.stats["LCK"] * 1.15)

    resumen, winner = fight(player, boss)
    return resumen, winner


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
