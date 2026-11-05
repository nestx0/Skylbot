import datetime
import random

from database.dataBase import getUser, updateUser
from database.plantsDatabase import PlantsDatabase
from plants.plantObjects import Inventario, Semilla

MAX_SHOP_SIZE = 12

intervalosRarezas = {
    "Common": [2500, 4500],
    "Uncommon": [6000, 8000],
    "Rare": [10000, 13450],
    "Epic": [15000, 20000],
}


class PlantShop:
    def __init__(self) -> None:
        self.shop = []
        self.prices = []
        self.size = MAX_SHOP_SIZE
        self.last_refresh: datetime.date | None = None
        # Al crearse por primera vez, forzamos el refresco inicial
        self.check_refresh()

    def check_refresh(self) -> bool:
        """Verifica si ha cambiado el día. Si es un día nuevo, regenera la tienda."""
        hoy = datetime.date.today()
        if self.last_refresh != hoy:
            self.refresh()
            self.last_refresh = hoy
            return True  # Indica que la tienda se ha renovado
        return False

    def refresh(self):
        """Genera un nuevo catálogo de semillas y precios."""
        self.shop = []
        self.prices = []
        for _ in range(self.size):
            s = Semilla.newSeed()
            precio = round(
                random.uniform(
                    intervalosRarezas[s.rarity][0], intervalosRarezas[s.rarity][1]
                )
            )
            self.prices.append(precio)
            self.shop.append(s)

    def buy(self, pos: int, userID: int) -> tuple[bool, str]:
        self.check_refresh()

        actualPos = pos - 1
        if actualPos < 0 or actualPos >= len(self.shop):
            return False, "Not available!"

        price = self.prices[actualPos]
        balance = getUser(userID)["balance"]

        if balance < price:
            return False, "Not enough balance to buy"

        rawInv = PlantsDatabase.getInventory(userID)
        inv = Inventario()
        inv.load(rawInv)

        item = self.shop[actualPos]
        name = item.nombre
        if not inv.add(item):
            return False, "Not enough space in your inventory"

        balance -= price
        updateUser(userID, balance)

        PlantsDatabase.updateInventory(userID, inv.toDict())
        self.shop.pop(actualPos)
        self.prices.pop(actualPos)

        return True, f"Congrats on buying {name}"


tienda = PlantShop()
