import random
from database.dataBase import getUser, updateUser

numbas = {
    "0": "green",   "1": "red",     "2": "black",   "3": "red",     "4": "black",   "5": "red",     "6": "black",
    "7": "red",     "8": "black",   "9": "red",     "10": "black",  "11": "black",  "12": "red",    "13": "black",
    "14": "red",    "15": "black",  "16": "red",    "17": "black",  "18": "red",    "19": "red",    "20": "black",
    "21": "red",    "22": "black",  "23": "red",    "24": "black",  "25": "red",    "26": "black",  "27": "red",
    "28": "black",  "29": "black",  "30": "red",    "31": "black",  "32": "red",    "33": "black",  "34": "red",
    "35": "black",  "36": "red"
}

options = [
    "red",      "black",    "green",
    "1st",      "2nd",      "3rd",
    "half1",    "half2",
    "numbers",
    "orphans",  "gserie",   "5/8",
    "zerozone"
]

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
            return result in [0, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35]
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
            case "gserie":
                return 36 / 16
            case "5/8":
                return 36 / 12
            case "zerozone":
                return 36 / 7
            case "orphans":
                return 36 / 8
    else:
        return 0

def getNumbers():
    return numbas


#====================================================================================================


async def roulette(ctx, amount, choice=None, *, numbers: str | None = None):
    balance = getUser(ctx.author.id)["balance"]
    numbas = getNumbers()
    if isinstance(amount, str) and amount.lower() == "allin":
        amount = balance
    else:
        try:
            amount = int(amount)
            if amount < 1:
                return await ctx.send("❌ You must bet at least 1 point.")
        except ValueError:
            return await ctx.send("❌ You must enter a number or 'allin'.")
    if amount > balance:
        return await ctx.send("❌ Not enough balance.")

    if amount and choice:
        if choice.lower() not in options:
            await ctx.send(
                "Select a valid option: \n *red*, *black*, *green*, \n *1st*, *2nd*, *3rd*, \n *half1*, *half2*, \n *orphans*, *gserie*, *5/8*, *zerozone*, \n *numbers*"
            )
            return
        elif choice != "numbers":
            result = random.randint(0, 36)
            updateUser(ctx.author.id, balance - amount)
            newBalance = getUser(ctx.author.id)["balance"]

            win = getWin(result, choice)

            mult = getMultiplier(win, choice)
            assert mult is not None
            amount = int(amount * mult)
            updateUser(ctx.author.id, newBalance + amount)
            if "red" in numbas[str(result)]:
                decor = "🔴"
            elif "black" in numbas[str(result)]:
                decor = "⚫"
            else:
                decor = "🟢"
            if win:
                await ctx.send(
                    f"Number chosen was {result} {decor}, you won {amount} bolivares"
                )
            else:
                await ctx.send(
                    f"Number chosen was {result} {decor}, better luck next time"
                )
        else:
            if not numbers:
                return await ctx.send(
                    "You must provide numbers to bet on when choosing 'numeros'"
                )
            try:
                chosen_numbers = [
                    int(num) for num in numbers.split(" ") if 0 <= int(num) <= 36
                ]
                if not chosen_numbers:
                    return await ctx.send(
                        "You must provide valid numbers between 0 and 36"
                    )
            except ValueError:
                return await ctx.send(
                    "Please provide numbers only, separated by spaces"
                )

            result = random.randint(0, 36)
            updateUser(ctx.author.id, balance - amount)
            newBalance = getUser(ctx.author.id)["balance"]
            if "red" in numbas[str(result)]:
                decor = "🔴"
            elif "black" in numbas[str(result)]:
                decor = "⚫"
            else:
                decor = "🟢"

            if result in chosen_numbers:
                mult = 36 / len(chosen_numbers)
                amount = round(amount * mult)
                updateUser(ctx.author.id, newBalance + amount)
                await ctx.send(
                    f"Number chosen was {result}{decor}, you won {amount} bolivares"
                )
            else:
                await ctx.send(
                    f"Number chosen was {result}{decor}, better luck next time"
                )