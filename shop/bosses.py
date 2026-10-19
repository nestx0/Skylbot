import copy

from shop.fights import fight
from shop.gacha import Character

bosses = [
    {
        "id": 1,
        "name": "Mr Balls",
        "desc": "The evil brother of Mr. Penis",
        "rarity": "Boss",
        "stats": {"HP": 1811, "ATK": 388, "DEF": 405, "SPE": 442, "LCK": 400},
        "lvl": 69,
        "image": "images/characters/mr_balls.webp",
    },
    {
        "id": 2,
        "name": "Pringles Floppa",
        "desc": "Copies all your stats, but better",
        "rarity": "Boss",
        "stats": {"HP": "???", "ATK": "???", "DEF": "???", "SPE": "???", "LCK": "???"},
        "lvl": "???",
        "image": "images/characters/pringles_floppa.webp",
    },
    {
        "id": 3,
        "name": "Hacienda",
        "desc": "Taking half your income, and stats",
        "rarity": "Boss",
        "stats": {"HP": 2026, "ATK": 300, "DEF": 350, "SPE": 1, "LCK": 7000},
        "lvl": 1,
        "image": "images/characters/hacienda.webp",
    },
]


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
