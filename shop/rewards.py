import random

from dataBase import *


class coinReward:
    def __init__(self, rarity: str):
        self.rarity = rarity

    def getAmount(self) -> int:
        ranges = {
            "Common": (3_000, 10_000),
            "Rare": (7_000, 18_000),
            "Epic": (10_000, 30_000),
            "Legendary": (50_000, 100_000),
        }
        low, high = ranges[self.rarity]
        return random.randint(low, high)

    def applyReward(self, userID):
        balance = getUser(userID)["balance"]
        reward = self.getAmount()
        newBalance = balance + reward
        updateUser(userID, newBalance)
        return reward


class powerUpReward:
    def __init__(self, rarity: str):
        self.rarity = rarity

    def getAmount(self):
        types = {
            "Common": 0,
            "Rare": 0.1,
            "Epic": 0.15,
            "Legendary": 0.3,
        }
        reward = types[self.rarity]

    # def applyReward(self, userID):
    # power = getUser["powerUp"]
    # updatePower(userID, power + self.getAmount())
