import discord
import random

from database.dataBase import getUser, updateUser
from .views import BlackjackView

def generarDeck():
    suits = ["♥️","♦️","♣️","♠️"]
    ranks = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    return [{"rank": r, "suit": s} for s in suits for r in ranks]

def shuffleDeck(deck):
    random.shuffle(deck)

def repartirCartasBJ(deck):

    manoJugador = {
        "cartas":[deck.pop(),deck.pop()],
        "puntuacion":0,
        "esBlackJack":False
    }

    manoDealer = {
        "cartas":[deck.pop(),deck.pop()],
        "puntuacion":0,
        "esBlackJack":False
    }

    return manoJugador, manoDealer

def calcularValor(mano):
    suma = 0
    ases = 0

    for carta in mano["cartas"]:
        valor = carta["rank"]
        if valor in ["J","Q","K"]:
            suma += 10
        elif valor == "A":
            suma += 11
            ases += 1
        else:
            suma += int(valor)
    while suma > 21 and ases > 0:
        suma -= 10
        ases -= 1   
    mano["puntuacion"] = suma
    mano["esBlackJack"] = len(mano["cartas"]) == 2 and suma == 21
    
def draw(deck):
    return deck.pop()

class BlackjackGame:
    def __init__(self, jugador, bet):
        self.jugador = jugador
        self.baraja = generarDeck()
        shuffleDeck(self.baraja)
        self.manoJugador, self.manoDealer = repartirCartasBJ(self.baraja)
        self.state = "Player Turn"
        calcularValor(self.manoDealer)
        calcularValor(self.manoJugador)
        self.verificarBJ()
        self.discordMessage = ""
        self.win = False
        self.bet = bet
    
    def verificarBJ(self):
        if self.manoJugador["esBlackJack"]:
            self.win = True
            self.state = "Finish"
            self.discordMessage = "You Won! 🃏"
    def generarEmbed(self):

        color =  discord.Color.green() if self.state == "Player Turn" else discord.Color.dark_blue()
        file = discord.File("assets/Duala_dealer.webp", filename="Duala_dealer.webp")

        embed = discord.Embed(
            title="🃏 Blackjack 🃏",
            color=color,
        )

        cartasJugador = " ".join(
        card["rank"] + card["suit"]
        for card in self.manoJugador["cartas"]
        )

        embed.add_field(
            name="Your Hand",
            value=f"{cartasJugador} ({self.manoJugador['puntuacion']})",
            inline=False 
        )

        if self.state == "Player Turn":
            cartaDealer = self.manoDealer["cartas"][0]
            cartasDealer = f"{cartaDealer['rank']}{cartaDealer['suit']} ?"
            puntuacion = self.manoDealer['cartas'][0]['rank']
        elif self.state == "Finish":
            cartasDealer = " ".join(
            card["rank"] + card["suit"]
            for card in self.manoDealer["cartas"]
            )
            puntuacion = self.manoDealer["puntuacion"]
        embed.add_field(
            name="Dealer's Hand",
            value=f"{cartasDealer} ({puntuacion})",
            inline=False 
        )

        self.getResult()
        embed.set_footer(text=self.discordMessage)
        embed.set_thumbnail(url="attachment://Duala_dealer.webp")

        return embed

    async def handleHit(self):

        self.manoJugador["cartas"].append(draw(self.baraja))
        calcularValor(self.manoJugador)
        if(self.manoJugador["puntuacion"] > 21):
            self.win = False
            self.state = "Finish"

    async def handleStand(self):

        self.state = "Dealer Turn"
        while(self.manoDealer["puntuacion"] < 17):
            self.manoDealer["cartas"].append(draw(self.baraja))
            calcularValor(self.manoDealer)
        if self.manoJugador["puntuacion"] > 21:
            self.win = False   
        elif self.manoDealer["puntuacion"] > 21:
            self.win = True    
        elif self.manoJugador["puntuacion"] >= self.manoDealer["puntuacion"]:
            self.win = True    
        else:
            self.win = False
        self.state = "Finish"
        

    def getResult(self):
        if self.win == True:
            self.discordMessage = "You Won! 🃏"
        else:
            if self.state == "Player Turn":
                self.discordMessage = "Try Hitting"
            elif self.state == "Dealer Turn":
                self.discordMessage = "Waiting"
            else:
                self.discordMessage = "You Lost! 🃏"


#====================================================================================================


async def blackjack(ctx, bet):
    balance = int(getUser(ctx.author.id)["balance"])
    file = discord.File("assets/Duala_dealer.webp", filename="Duala_dealer.webp")

    if isinstance(bet, str) and bet.lower() == "allin":
        bet = balance
    else:
        try:
            bet = int(bet)
            if bet < 1:
                return await ctx.send("❌ You must bet at least 1 point.")
        except ValueError:
            return await ctx.send("❌ You must enter a number or 'allin'.")
    if bet > balance:
        return await ctx.send("❌ Not enough balance.")

    updateUser(ctx.author.id, balance - bet)

    game = BlackjackGame(ctx.author, bet)
    view = BlackjackView(game)
    await ctx.send(embed=game.generarEmbed(), view=view, file=file)

    balance += bet


async def jackblack(ctx, *, msg):
    await ctx.send(file=discord.File("assets/jack-black-minecraft.gif"))