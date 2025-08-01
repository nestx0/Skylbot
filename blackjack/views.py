import discord
from discord.ui import Button, View
from dataBase import getUser, updateUser

class BlackjackView(View):
    def __init__(self, juego):
        super().__init__(timeout=120.0)
        self.juego = juego  

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def pedirCarta(self, interaction, button):
        if self.juego.jugador == interaction.user:
            await self.juego.handleHit()
            newEmbed = self.juego.generarEmbed()
            view = self
            if self.juego.state == "Finish":
                view = None
            await interaction.response.edit_message(embed=newEmbed, view=view)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def plantarse(self, interaction, button):
        if self.juego.jugador ==  interaction.user:
            await self.juego.handleStand()
            newEmbed = self.juego.generarEmbed()
            view = self
            if self.juego.state == "Finish":
                view = None
                if self.juego.win:
                    self.juego.bet *= 2
                else:
                    self.juego.bet = 0
                balance = getUser(interaction.user.id)["balance"]
                updateUser(interaction.user.id, balance+self.juego.bet)

            await interaction.response.edit_message(embed=newEmbed, view=view)
        else:
            await interaction.response.send_message("Not your turn", ephemeral=True)
            return