import datetime
import random

RARITIES = ["Common", "Uncommon", "Rare", "Epic"]
WEIGHTS = [60, 25, 10, 5]
MAX_VALUE = 500000
MAX_INVENTORY = 20
MIN_MULT = 1.3
MAX_MULT = 1.8
BASE_VALUES = {"Common": 1000, "Uncommon": 2500, "Rare": 5000, "Epic": 10000}

ADJETIVES = [
    "Cosmic",
    "Quantum",
    "Lazy",
    "Toasted",
    "Shiny",
    "Furious",
    "Frozen",
    "Spicy",
    "Invisible",
    "Plump",
    "Majestic",
    "Squeaky",
    "Stinky",
    "Sacred",
    "Rusty",
    "Wild",
    "Thirsty",
    "Sleepy",
    "Hairy",
    "Sticky",
    "Shivering",
    "Brave",
    "Primal",
    "Epic",
    "Tiny",
    "Absurd",
    "Secret",
    "Galactic",
    "Flaming",
    "Cuddly",
    "Radioactive",
    "Legendary",
    "Sweaty",
    "Fluffy",
    "Mystical",
]

NOUNS = [
    "Cheese",
    "Abyss",
    "Fire",
    "Sock",
    "Destiny",
    "Duck",
    "Universe",
    "Chicken",
    "Dream",
    "Chaos",
    "Mystery",
    "Pants",
    "Ice",
    "Dragon",
    "Donut",
    "Silence",
    "Shadow",
    "Broccoli",
    "Space",
    "Thunder",
    "Banana",
    "Echo",
    "Magic",
    "Hat",
    "Shoe",
    "Noodle",
    "Potato",
    "Heart",
    "Juice",
    "Whisper",
    "Mirage",
    "Mustard",
    "Lightning",
    "Wind",
    "Slipper",
    "Surge",
    "Dispair",
    "Doom",
]

FLOWERS = [
    "Rose",
    "Daisy",
    "Sunflower",
    "Tulip",
    "Orchid",
    "Lily",
    "Carnation",
    "Hydrangea",
    "Peony",
    "Chrysanthemum",
    "Dahlia",
    "Jasmine",
    "Poppy",
    "Lotus",
    "Lavender",
    "Hibiscus",
    "Begonia",
    "Camellia",
    "Violet",
    "Geranium",
    "Wither Rose",
]


def getRandomName():
    return random.choice(ADJETIVES), random.choice(NOUNS)


class ItemInventario:
    def __init__(self, nombre: str = "???") -> None:
        self.esSemilla = False
        self.nombre = nombre

    @classmethod
    def createFromDict(cls, data: dict):
        """Factory method que decide si crear una Planta o una Semilla."""
        if data.get("esSemilla"):
            return Semilla.fromDict(data)
        return Planta.fromDict(data)


class Semilla(ItemInventario):
    def __init__(self, rareza: str, nombre=None) -> None:
        if nombre is None:
            adj, noun = getRandomName()
            nombre = f"Seed of {adj} {noun}"

        super().__init__(nombre)
        self.esSemilla = True
        self.rarity = rareza

    def germinar(self):
        r = round(random.uniform(MIN_MULT, MAX_MULT), 3)
        nombre_base = self.nombre.replace("Seed of ", "")
        flower = random.choice(FLOWERS)
        nombre_planta = f"{flower} of {nombre_base}"
        return Planta(rarity=self.rarity, razon=r, nombre=nombre_planta)

    def toDict(self):
        return {"name": self.nombre, "esSemilla": self.esSemilla, "rarity": self.rarity}

    @classmethod
    def fromDict(cls, data: dict):
        return cls(rareza=data["rarity"], nombre=data["name"])

    @classmethod
    def newSeed(cls):
        rarity = random.choices(RARITIES, weights=WEIGHTS, k=1)[0]
        return cls(rarity)


class Planta(ItemInventario):
    def __init__(
        self,
        rarity: str,
        lastTimeWater=None,
        nombre=None,
        lvl: int = 1,
        racha: int = 0,
        razon: float = 1.3,
        varianza: float | None = None,
    ) -> None:
        if lastTimeWater is None:
            lastTimeWater = datetime.date.today()

        if nombre is None:
            adj, noun = getRandomName()
            plant = random.choice(FLOWERS)
            nombre = f"{plant} of {adj} {noun}"

        super().__init__(nombre)
        self.lvl = lvl
        self.rarity = rarity
        self.racha = racha
        self.lastTimeWater = lastTimeWater
        self.razon = razon

        if varianza is None:
            self.varianza = max(0.5, self.razon - random.uniform(0.05, 0.5))
        else:
            self.varianza = varianza

    @property
    def value(self):
        val = int(
            BASE_VALUES[self.rarity]
            * self.varianza
            * (self.lvl**self.razon)
            * (1 + float(self.racha / 10))
        )
        return min(val, MAX_VALUE)

    def grow(self) -> bool:
        hoy = datetime.date.today()
        ayer = hoy - datetime.timedelta(days=1)

        if self.value >= MAX_VALUE or self.lastTimeWater == hoy:
            return False

        self.lvl += 1

        if self.lastTimeWater == ayer:
            self.racha += 1
        else:
            self.racha = 1

        self.lastTimeWater = hoy
        return True

    def toDict(self):
        return {
            "lvl": self.lvl,
            "name": self.nombre,
            "esSemilla": self.esSemilla,
            "rarity": self.rarity,
            "racha": self.racha,
            "lastTime": self.lastTimeWater.isoformat() if self.lastTimeWater else None,
            "razon": self.razon,
            "varianza": self.varianza,
        }

    @classmethod
    def fromDict(cls, data: dict):
        fecha_str = data.get("lastTime")
        fechaObj = datetime.date.fromisoformat(fecha_str) if fecha_str else None
        return cls(
            rarity=data["rarity"],
            nombre=data["name"],
            lvl=data.get("lvl", 1),
            racha=data.get("racha", 0),
            lastTimeWater=fechaObj,
            razon=data.get("razon", 1.3),
            varianza=data.get("varianza", None),
        )


class Inventario:
    def __init__(self) -> None:
        self.inventory = []
        self.max = MAX_INVENTORY

    def add(self, p) -> bool:
        if len(self.inventory) >= self.max:
            return False

        self.inventory.append(p)
        return True

    def sell(self, pos: int):
        actualPos = pos - 1
        if actualPos < 0 or actualPos >= len(self.inventory):
            return False, 0

        item = self.inventory[actualPos]
        if item.esSemilla:
            return False, 0

        value = item.value
        self.inventory.pop(actualPos)
        return True, value

    def toDict(self):
        return [item.toDict() for item in self.inventory]

    def load(self, dataList):
        self.inventory = []
        for item_data in dataList:
            nuevo_item = ItemInventario.createFromDict(item_data)
            self.inventory.append(nuevo_item)
