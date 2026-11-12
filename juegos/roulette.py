import random
from pathlib import Path

from command_utils import parse_amount
import discord

from database.dataBase import getUser, updateUser


numbas = {
    "0": "green", "1": "red", "2": "black", "3": "red", "4": "black", "5": "red", "6": "black",
    "7": "red", "8": "black", "9": "red", "10": "black", "11": "black", "12": "red", "13": "black",
    "14": "red", "15": "black", "16": "red", "17": "black", "18": "red", "19": "red", "20": "black",
    "21": "red", "22": "black", "23": "red", "24": "black", "25": "red", "26": "black", "27": "red",
    "28": "black", "29": "black", "30": "red", "31": "black", "32": "red", "33": "black", "34": "red",
    "35": "black", "36": "red"
}

options = [
    "red", "black", "green",
    "1st", "2nd", "3rd",
    "half1", "half2",
    "numbers",
    "orphans", "gserie", "5/8",
    "zerozone"
]

COLOR_DATA = {"red": (0xE74C3C, "🔴"), "black": (0x2B2D31, "⚫"), "green": (0x2ECC71, "🟢")}


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
    return 0


def getNumbers():
    return numbas


def _animation_path(color: str) -> Path | None:
    filename = f"roulette_{color}.webp"
    for parent in Path(__file__).resolve().parents:
        path = parent / "assets" / "roulette" / filename
        if path.is_file():
            return path
    return None


#========================================================================================================================================


async def roulette(ctx, amount, choice=None, *, numbers: str | None = None):
    balance = getUser(ctx.author.id)["balance"]

    try:
        amount = parse_amount(amount, balance, allow_allin=True)
    except ValueError as exc:
        return await ctx.send(f"❌ {exc}")

    if amount < 1:
        return await ctx.send("❌ You must bet at least 1 point.")
    if amount > balance:
        return await ctx.send("❌ Not enough balance.")

    if not choice or choice.lower() not in options:
        return await ctx.send(
            "Select a valid option:\n"
            "*red*, *black*, *green*,\n"
            "*1st*, *2nd*, *3rd*,\n"
            "*half1*, *half2*,\n"
            "*orphans*, *gserie*, *5/8*, *zerozone*,\n"
            "*numbers*"
        )

    choice = choice.lower()
    chosen_numbers = None
    if choice == "numbers":
        if not numbers:
            return await ctx.send("You must provide numbers to bet on when choosing 'numbers'.")
        try:
            chosen_numbers = [int(num) for num in numbers.split() if 0 <= int(num) <= 36]
        except ValueError:
            return await ctx.send("Please provide numbers only, separated by spaces.")
        if not chosen_numbers:
            return await ctx.send("You must provide valid numbers between 0 and 36.")

    result = random.randint(0, 36)
    color = numbas[str(result)]
    animation = _animation_path(color)
    if animation is None:
        return await ctx.send(f"❌ Missing animation: assets/roulette/roulette_{color}.webp")

    win = getWin(result, choice, chosen_numbers)
    multiplier = getMultiplier(win, choice, chosen_numbers)
    payout = round(amount * multiplier) if choice == "numbers" else int(amount * multiplier)
    new_balance = balance - amount + payout
    updateUser(ctx.author.id, new_balance)

    embed_color, symbol = COLOR_DATA[color]
    embed = discord.Embed(
        title="Roulette",
        description=(
            f"**Number: {result} {symbol}**\n"
            f"{'You won ' + str(payout) + ' bolivares!' if win else 'Better luck next time!'}"
        ),
        color=embed_color,
    )
    embed.add_field(name="Bet", value=f"{amount} bolivares", inline=True)
    embed.add_field(name="Balance", value=f"{new_balance} bolivares", inline=True)
    embed.set_thumbnail(url=f"attachment://{animation.name}")
    await ctx.send(embed=embed, file=discord.File(animation, filename=animation.name))
