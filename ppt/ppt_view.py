import discord
from ppt.ppt_game import PPTGame
from dataBase import getUser, updateUser

class PPTView(discord.ui.View):
    def __init__(self, user_id, amount: int):
        super().__init__(timeout=120.0)
        self.user_id = user_id
        self.amount = amount

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.primary, emoji="🪨")
    async def rock_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "Rock")

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.primary, emoji="📄")
    async def paper_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "Paper")

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.primary, emoji="✂️")
    async def scissors_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "Scissors")

    async def handle_choice(self, interaction: discord.Interaction, player_choice: str):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Don't touch!", ephemeral=True)

        bot_choice = PPTGame.get_bot_choice()
        result = PPTGame.determine_winner(player_choice, bot_choice)

        if result == "player":
            self.amount *= 2
            result_msg = f"You won! 🎉 You've obtained {self.amount} bolivares"
        elif result == "draw":
            result_msg = "Draw! 🤝"
        else:
            result_msg = "You lost! <:Rs_JAJAJA:1377299177813311571> "
            self.amount = 0


        balance = getUser(self.user_id)["balance"]
        updateUser(self.user_id, balance + self.amount)

        embed = discord.Embed(
            title="Game Results",
            description=f"You've chosen {PPTGame.OPTIONS[player_choice]} {player_choice}\n"
                        f"Duala has chosen {PPTGame.OPTIONS[bot_choice]} {bot_choice}\n\n"
                        f"**{result_msg}**",
            color=discord.Color.green() if result == "player" else
                discord.Color.blue() if result == "draw" else
                discord.Color.red()
        )

        embed.set_thumbnail(url="attachment://Duala_dealer.png")

        return await interaction.response.edit_message(embed=embed, view=None)
