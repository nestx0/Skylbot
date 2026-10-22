from juegos.blackjack.cards import generarDeck, shuffleDeck, repartirCartasBJ, calcularValor, draw
import discord

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
    


