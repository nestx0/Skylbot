numbas = {
    "0": "green",
    "1": "red",
    "2": "black",
    "3": "red",
    "4": "black",
    "5": "red",
    "6": "black",
    "7": "red",
    "8": "black",
    "9": "red",
    "10": "black",
    "11": "black",
    "12": "red",
    "13": "black",
    "14": "red",
    "15": "black",
    "16": "red",
    "17": "black",
    "18": "red",
    "19": "red",
    "20": "black",
    "21": "red",
    "22": "black",
    "23": "red",
    "24": "black",
    "25": "red",
    "26": "black",
    "27": "red",
    "28": "black",
    "29": "black",
    "30": "red",
    "31": "black",
    "32": "red",
    "33": "black",
    "34": "red",
    "35": "black",
    "36": "red",
}


# Bro la win function es la leche
def getWin(result: int, choice: str, numbers: list | None = None):
    match choice:
        case "red":
            return numbas[str(result)] == "red"
        case "black":
            return numbas[str(result)] == "black"
        case "green" | "0":
            return result == 0
        case "1st":
            return 1 <= result <= 12
        case "2nd":
            return 13 <= result <= 24
        case "3rd":
            return 25 <= result <= 36
        case "half1":
            return 1 <= result <= 18
        case "half2":
            return 19 <= result <= 36
        case "gserie":
            return result in [
                0,
                3,
                4,
                7,
                12,
                15,
                18,
                19,
                21,
                22,
                25,
                26,
                28,
                29,
                32,
                35,
            ]
        case "5/8":
            return result in [5, 8, 10, 11, 13, 16, 23, 24, 27, 30, 33, 36]
        case "zerozone":
            return result in [0, 3, 12, 15, 26, 32, 35]
        case "orphans":
            return result in [1, 6, 9, 14, 17, 20, 31, 34]
        case "numbers":
            if numbers is not None:
                return result in map(int, numbers)

    return False


def getMultiplier(win: bool, choice: str, numbers: list | None = None):
    if win:
        match choice:
            case "red" | "black" | "half1" | "half2":
                return 2
            case "1st" | "2nd" | "3rd":
                return 3
            case "green" | "0":
                return 36
            case "numbers":
                if numbers is not None:
                    return 36 / len(numbers)
            case "gran serie":
                return 36 / 16
            case "serie 5/8":
                return 36 / 12
            case "zona cero":
                return 36 / 7
            case "huerfanos":
                return 36 / 8
    else:
        return 0


def getNumbers():
    return numbas
