import copy

from shop.fights import fight
from shop.gacha import Character

stats = ["ATK", "DEF", "SPE", "LCK", "HP"]
RARITY_INCREASED_STATS = 4

bosses = [
    {
        "id": 1,
        "name": "Mr Balls",
        "desc": "The evil brother of Mr. Penis",
        "rarity": "Boss",
        "stats": {"HP": 1811, "ATK": 388, "DEF": 405, "SPE": 442, "LCK": 400},
        "lvl": 69,
        "image": "assets/characters/mr_balls.webp",
    },
    {
        "id": 2,
        "name": "Pringles Floppa",
        "desc": "Copies all your stats, but better",
        "rarity": "Boss",
        "stats": {"HP": "???", "ATK": "???", "DEF": "???", "SPE": "???", "LCK": "???"},
        "lvl": "???",
        "image": "assets/characters/pringles_floppa.webp",
    },
    {
        "id": 3,
        "name": "Hacienda",
        "desc": "Taking half your income, and stats",
        "rarity": "Boss",
        "stats": {"HP": 2026, "ATK": 300, "DEF": 350, "SPE": 1, "LCK": 7000},
        "lvl": 1,
        "image": "assets/characters/hacienda.webp",
    },
    {
        "id": 4,
        "name": "Furina",
        "desc": "Hydro Archon (?)",
        "rarity": "Boss",
        "stats": {"HP": 3000, "ATK": 255, "DEF": 140, "SPE": 300, "LCK": 1000},
        "lvl": 1,
        "image": "assets/characters/furina.webp",
    },
    {
        "id": 5,
        "name": "Jagger Cat",
        "desc": "Close to knocked out",
        "rarity": "Boss",
        "stats": {"HP": 1000, "ATK": 1000, "DEF": 30, "SPE": 370, "LCK": 67},
        "lvl": 1,
        "image": "assets/characters/jaggercat.webp",
    },
    {
        "id": 6,
        "name": "Tired Teto",
        "desc": "Tired of life",
        "rarity": "Boss",
        "stats": {"HP": 1789, "ATK": 333, "DEF": 700, "SPE": 105, "LCK": 1},
        "lvl": 1,
        "image": "assets/characters/tiredteto.webp",
    },
    {
        "id": 7,
        "name": "Net and Yahu",
        "desc": "They are who you thing they are",
        "rarity": "Boss",
        "stats": {"HP": 2222, "ATK": 372, "DEF": 302, "SPE": 222, "LCK": 222},
        "lvl": 1,
        "image": "assets/characters/netandyahu.webp",
    },
]


class Boss(Character):
    def apply_pre_fight_effect(self, char: Character) -> str:
        return ""

    @classmethod
    def from_dict(cls, info):
        boss_classes = {
            "Mr Balls": MrBallsBoss,
            "Pringles Floppa": PringlesFloppaBoss,
            "Hacienda": HaciendaBoss,
            "Jagger Cat": JaggerCatBoss,
            "Tired Teto": TiredTetoBoss,
            "Furina": FurinaBoss,
            "Net and Yahu": NetAndYahuBoss,
        }

        target_class = boss_classes.get(info.get("name", ""), cls)
        return target_class(info)


class MrBallsBoss(Boss):
    def apply_pre_fight_effect(self, char: Character) -> str:
        return super().apply_pre_fight_effect(char)


class HaciendaBoss(Boss):
    def apply_pre_fight_effect(self, char: Character) -> str:
        statsMultiplier(char, 0.5)
        return "Hacienda halved all your stats"


class PringlesFloppaBoss(Boss):
    def apply_pre_fight_effect(self, char: Character) -> str:
        self.stats = copy.deepcopy(char.stats)
        statsMultiplier(self, 1.15)
        return "Pringles Floppa copied your stats 15% better"


class FurinaBoss(Boss):
    def apply_pre_fight_effect(self, char: Character) -> str:
        msg = ""
        if char.rarity != "Rare":
            statsMultiplier(self, RARITY_INCREASED_STATS)
            msg += "Due to your char rarity, Furina got 4 times stronger !"

        return msg


class TiredTetoBoss(Boss):
    def apply_pre_fight_effect(self, char: Character) -> str:
        msg = ""
        if char.rarity != "Common":
            statsMultiplier(self, RARITY_INCREASED_STATS)
            msg += "Due to your char rarity, Teto got 4 times stronger !"

        return msg


class JaggerCatBoss(Boss):
    def apply_pre_fight_effect(self, char: Character) -> str:
        msg = ""
        if char.rarity != "Uncommon":
            statsMultiplier(self, RARITY_INCREASED_STATS)
            msg += "Due to your char rarity, Jagger Cat got 4 times stronger !"

        return msg


class NetAndYahuBoss(Boss):
    def apply_pre_fight_effect(self, char: Character) -> str:
        msg = ""
        if char.rarity != "Epic":
            statsMultiplier(self, RARITY_INCREASED_STATS)
            msg += "Due to your char rarity, Net and Yahu got 4 times stronger !"

        return msg


# Hacer 4 bosses, uno que cuadruplique sus estadísticas * 4


def bossHandler(charP, option: int):
    player = copy.deepcopy(charP)
    boss_raw = copy.deepcopy(bosses[option - 1])

    boss = Boss.from_dict(boss_raw)
    msg = boss.apply_pre_fight_effect(player) + "\n"

    resumen, winner = fight(player, boss)
    return msg + resumen, winner


def statsMultiplier(char: Character, mult: float):

    assert char.stats is not None
    for stat in stats:
        char.stats[stat] = round(char.stats[stat] * mult)
