import json
import random
import copy

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
    {
        "id": 15,
        "name": "Blub Cat",
        "desc": "Doesn't care what you think, he has his one and only thought",
        "rarity": "Common",
        "stats": {"HP": 10, "ATK": 2, "DEF": 3, "SPE": 4, "LCK": 1},
        "lvl": 1,
        "image": "images/characters/blub_cat.jpeg",
    },
    {          
        "id": 17,
        "name": "Emo Cat",
        "desc": "Listens to Linkin Park all day",
        "rarity": "Common",
        "stats": {"HP": 9, "ATK": 4, "DEF": 1, "SPE": 4, "LCK": 1},
        "lvl": 1,
        "image": "images/characters/emo_cat.jpeg",
    },
    {          
        "id": 23,
        "name": "Miguel",
        "desc": "My pana Miguel",
        "rarity": "Common",
        "stats": {"HP": 9, "ATK": 4, "DEF": 2, "SPE": 2, "LCK": 2},
        "lvl": 1,
        "image": "images/characters/miguel.jpeg",
    },
    {          
        "id": 24,
        "name": "Nom Cat",
        "desc": "He's about to get eaten, help him !!!",
        "rarity": "Common",
        "stats": {"HP": 10, "ATK": 3, "DEF": 1, "SPE": 1, "LCK": 5},
        "lvl": 1,
        "image": "images/characters/nom_cat.jpeg",
    },
    {          
        "id": 27,
        "name": "Smiling Cat",
        "desc": "She's just happy to be out there",
        "rarity": "Common",
        "stats": {"HP": 11, "ATK": 1, "DEF": 4, "SPE": 2, "LCK": 3},
        "lvl": 1,
        "image": "images/characters/smile_cat.jpeg",
    },
    {
        "id": 31,
        "name": "Goblin Head Chef",
        "desc": "Kids, what do you want for dinner tonight?",
        "rarity": "Common",
        "stats": {"HP": 8, "ATK": 2, "DEF": 3, "SPE": 3, "LCK": 2},
        "lvl": 1,
        "image": "images/characters/GoblinHeadChef.jpeg",
    }
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
    {
        "id": 14,
        "name": "Big Floppa",
        "desc": "The OG big cat of the internet",
        "rarity": "Uncommon",
        "stats": {"HP": 17, "ATK": 5, "DEF": 5, "SPE": 4, "LCK": 1},
        "lvl": 1,
        "image": "images/characters/big_floppa.jpeg",
    },
    {          
        "id": 18,
        "name": "About-To-Explode Cat",
        "desc": "He's one step away from recreating Hiroshima",
        "rarity": "Uncommon",
        "stats": {"HP": 15, "ATK": 8, "DEF": 2, "SPE": 3, "LCK": 2},
        "lvl": 1,
        "image": "images/characters/explode_cat.jpeg",
    },
    {
        "id": 22,
        "name": "Jett (Low-poly)",
        "desc": "BAN-BANG-BAN-BANF!",
        "rarity": "Uncommon",
        "stats": {"HP": 15, "ATK": 10, "DEF": 2, "SPE": 2, "LCK": 1},
        "lvl": 1,
        "image": "images/characters/Low-polyJett.jpeg",
    },
    {          
        "id": 28,
        "name": "Tiny Cat",
        "desc": "Not smaller than a microbio tho",
        "rarity": "Uncommon",
        "stats": {"HP": 13, "ATK": 3, "DEF": 1, "SPE": 10, "LCK": 1},
        "lvl": 1,
        "image": "images/characters/tiny_cat.jpeg",
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
    {        
        "id": 13,
        "name": "大开门 (Da Kai Men)",
        "desc": "Carrot or tissue? Asking for a friend...",
        "rarity": "Rare",
        "stats": {"HP": 23, "ATK": 2, "DEF": 3, "SPE": 8, "LCK": 12},
        "lvl": 1,
        "image": "images/characters/DaKaiMen.jpeg",
    },
    {          
        "id": 20,
        "name": "Joker Cat",
        "desc": "We live in a society...",
        "rarity": "Rare",
        "stats": {"HP": 20, "ATK": 5, "DEF": 4, "SPE": 8, "LCK": 8},
        "lvl": 1,
        "image": "images/characters/joker_cat.jpeg",
    },
    {          
        "id": 69,
        "name": "Mr Penis",
        "desc": "MR PENIS HIMSELF!!!",
        "rarity": "Rare",
        "stats": {"HP": 21, "ATK": 6, "DEF": 9, "SPE": 6, "LCK": 4},
        "lvl": 1,
        "image": "images/characters/mr_penis.jpeg",
    },
]

personajesEpico = [
    {        
        "id": 16,
        "name": "Counter-Terrorist Cat",
        "desc": "His skills came from playing CS2 all day long",
        "rarity": "Epic",
        "stats": {"HP": 35, "ATK": 10, "DEF": 15, "SPE": 8, "LCK": 10},
        "lvl": 1,
        "image": "images/characters/cs_cat.jpeg",
    },
    {          
        "id": 19,
        "name": "Floppa Whatsapp",
        "desc": "Evolved version of Floppa. He learnt how to use stickers",
        "rarity": "Epic",
        "stats": {"HP": 35, "ATK": 15, "DEF": 8, "SPE": 15, "LCK": 4},
        "lvl": 1,
        "image": "images/characters/floppa_whatsapp.jpeg",
    },
    {          
        "id": 21,
        "name": "Juan",
        "desc": "Juan",
        "rarity": "Epic",
        "stats": {"HP": 38, "ATK": 7, "DEF": 22, "SPE": 10, "LCK": 1},
        "lvl": 1,
        "image": "images/characters/juan.jpeg",
    },
    {          
        "id": 26,
        "name": "Obscure Cat",
        "desc": "It knows your deepest secrets",
        "rarity": "Epic",
        "stats": {"HP": 35, "ATK": 24, "DEF": 10, "SPE": 10, "LCK": 2},
        "lvl": 1,
        "image": "images/characters/obscure_cat.jpeg",
    },
]

bosses = [
    {          
        "id": 1,
        "name": "Mr Balls",
        "desc": "The evil brother of Mr. Penis",
        "rarity": "Boss",
        "stats": {"HP": 1811, "ATK": 388, "DEF": 405, "SPE": 442, "LCK": 400},
        "lvl": 69, 
        "image": "images/characters/mr_balls.jpeg",
    },
    {     
        "id": 2,
        "name": "Pringles Floppa",
        "desc": "Copies all your stats, but better",
        "rarity": "Boss",
        "stats": {"HP": "???", "ATK": "???", "DEF": "???", "SPE": "???", "LCK": "???"},
        "lvl": "???",
        "image": "images/characters/pringles_floppa.jpeg",
    },
    {          
        "id": 3,
        "name": "Hacienda",
        "desc": "Taking half your income, and stats",
        "rarity": "Boss",
        "stats": {"HP": 2026, "ATK": 300, "DEF": 350, "SPE": 1, "LCK": 7000},
        "lvl": 1,
        "image": "images/characters/hacienda.jpeg",
    },
    
]


def pullChar(userID):
    rarity = random.randint(0, 100)
    inventory = getInventory(userID)

    if rarity >= 0 and rarity <= 60:
        char = Character(random.choice(personajesComun))
    elif rarity > 60 and rarity <= 85:
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
        embed.add_field(name="\u200b", value="\u200b", inline=True) #Invisible field

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

        for stat, valor in boss.stats.items():
            embed.add_field(name=stat, value=str(valor), inline=True)
        embed.add_field(name="LVL", value=str(boss.level))

        embed.set_image(url="attachment://boss.jpeg")
        
        embed.set_footer(text=f"Boss {boss_id} out of {len(self.data)} | Use *boss fight {boss_id} to challenge!")

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

    firstStat = random.choice(stats)
    secondStat = random.choice(stats)
    thirdStat = random.choice(stats)
    fourthStat = random.choice(stats)

    char.level += 1

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
    frenzy_multiplier = 1.0 # En lugar de *= 2, le sumaremos 0.3 cada turno

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

        dodge_chance = min(25.0, (defender.stats["SPE"] / attacker.stats["SPE"]) * 5 + (defender.stats["LCK"] / 20))
        
        if random.uniform(0, 100) < dodge_chance:
            resumen += f"🛡️ **Turn {turno}:** {defender.name} gracefully dodged the attack!\n"
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

            final_dmg = round(base_dmg * varianza * multiplicador_crit * desperation_mult * frenzy_multiplier)
            if final_dmg < 1: final_dmg = 1
                
            defender.stats["HP"] -= final_dmg
            if defender.stats["HP"] < 0: defender.stats["HP"] = 0

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
    boss_raw = copy.deepcopy(bosses[option-1])

    boss = Character(boss_raw)

    if boss.name == "Hacienda":
        player.stats["HP"] /= 2
        player.stats["ATK"] /= 2
        player.stats["DEF"] /= 2
        player.stats["SPE"] /= 2
        player.stats["LCK"] /= 2
    if boss.name == "Pringles Floppa":
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

