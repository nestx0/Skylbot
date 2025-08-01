import random

def getWin(result: int, choice: str):
    if choice == "red" and result % 2 != 0:
        return True
    if choice == "black" and result % 2 == 0 and result != 0:
        return True
    if choice == "green" and result == 0:
        return True
    if choice == "1st" and (result >= 1 and result <= 12):
        return True
    if choice == "2nd" and (result >= 13 and result <= 24):
        return True
    if choice == "3rd" and (result >= 25 and result <= 36):
        return True
    if choice == "half1" and (result >= 1 and result <= 18):
        return True
    if choice == "half2" and (result >= 19 and result <= 36):
        return True
    return False

def getMultiplier(win: bool, choice: str):
    if win:
        if choice in ["red","black", "half1", "half2"]:
            return 2
        if choice in ["1st", "2nd", "3rd"]:
            return 3
        if choice == "green":
            return 36
    else:
        return 0