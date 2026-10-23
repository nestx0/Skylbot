import discord
import random
from database.dataBase import getUser, updateUser

class PPT(discord.ui.View):

    OPTIONS = {
        "Rock": "🪨",
        "Paper": "📄",
        "Scissors": "✂️"
    }

    WIN_CONDITIONS = {
        "Rock": "Scissors",
        "Paper": "Rock",
        "Scissors": "Paper"
    }

    @classmethod
    def get_bot_choice(cls):
        return random.choice(list(cls.OPTIONS.keys()))


    @classmethod
    def determine_winner(cls, player_choice, bot_choice):
        if player_choice == bot_choice:
            return "draw"
        if cls.WIN_CONDITIONS[player_choice] == bot_choice:
            return "player"
        return "bot"


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

        bot_choice = PPT.get_bot_choice()
        result = PPT.determine_winner(player_choice, bot_choice)

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
            description=f"You've chosen {PPT.OPTIONS[player_choice]} {player_choice}\n"
                        f"Duala has chosen {PPT.OPTIONS[bot_choice]} {bot_choice}\n\n"
                        f"**{result_msg}**",
            color=discord.Color.green() if result == "player" else
                discord.Color.blue() if result == "draw" else
                discord.Color.red()
        )

        embed.set_thumbnail(url="attachment://Duala_dealer.webp")

        return await interaction.response.edit_message(embed=embed, view=None)


#====================================================================================================


async def ppt(ctx, amount: str):
    bet_amount = 0
    balance = getUser(ctx.author.id)["balance"]
    balance = str(balance)
    if isinstance(amount, str) and amount.lower() == "allin":
        bet_amount = int(balance)
    else:
        try:
            bet_amount = int(amount)
            if bet_amount < 1:
                return await ctx.send("❌ You must bet at least 1 point.")
        except ValueError:
            return await ctx.send("❌ You must enter a number or 'allin'.")
    if bet_amount > int(balance):
        return await ctx.send("❌ Not enough balance.")
    newBalance = int(balance) - bet_amount
    updateUser(ctx.author.id, newBalance)

    embed = discord.Embed(
        title="Rock, Paper, Scissors",
        description="Click to start🤯",
        color=discord.Color.blue(),
    )
    view = PPT(ctx.author.id, bet_amount)
    embed.set_thumbnail(url="attachment://Duala_dealer.webp")
    file = discord.File("assets/Duala_dealer.webp", filename="Duala_dealer.webp")
    await ctx.send(embed=embed, view=view, file=file)