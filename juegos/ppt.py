import asyncio
import random
import discord

from discord.ext import commands
from database.dataBase import getUser, updateUser


OPTIONS = {"Rock": "🪨", "Paper": "📄", "Scissors": "✂️"}
WIN_CONDITIONS = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}


class ChoiceButton(discord.ui.Button):
    def __init__(self, choice: str):
        super().__init__(label=choice, emoji=OPTIONS[choice], style=discord.ButtonStyle.primary)
        self.choice = choice

    async def callback(self, interaction: discord.Interaction):
        await self.view.choose(interaction, self.choice)


class PPT(discord.ui.View):
    def __init__(self, user_id: int, amount: int):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.amount = amount
        self.finished = False
        self.lock = asyncio.Lock()
        self.message = None
        for choice in OPTIONS:
            self.add_item(ChoiceButton(choice))

    async def on_timeout(self):
        async with self.lock:
            if self.finished:
                return
            self.finished = True
            updateUser(self.user_id, int(getUser(self.user_id)["balance"]) + self.amount)
            if self.message:
                try:
                    await self.message.edit(content="Time expired. Your bet has been refunded.", view=None)
                except discord.HTTPException:
                    pass
        self.stop()

    async def choose(self, interaction: discord.Interaction, choice: str):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This is not your game.", ephemeral=True)
        async with self.lock:
            if self.finished:
                return await interaction.response.send_message("This game has already ended.", ephemeral=True)
            self.finished = True
            bot = random.choice(list(OPTIONS))
            result = 0 if choice == bot else 1 if WIN_CONDITIONS[choice] == bot else 2
            payout = self.amount if result == 0 else 2 * self.amount if result == 1 else 0
            if payout:
                updateUser(self.user_id, int(getUser(self.user_id)["balance"]) + payout)
            label = "Draw! Your bet has been refunded" if result == 0 else "You won!" if result == 1 else "You lost!"
            embed = discord.Embed(
                title="Rock, Paper, Scissors — Results",
                description=(f"You: {OPTIONS[choice]} {choice}\n"
                             f"Bot: {OPTIONS[bot]} {bot}\n\n"
                             f"**{label}** — you receive {payout} bolivars."),
                color=discord.Color.blue(),
            )
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()


class PPTDuel(discord.ui.View):
    def __init__(self, challenger: discord.Member, opponent: discord.Member, bet: int):
        super().__init__(timeout=120)
        self.challenger = challenger
        self.opponent = opponent
        self.bet = bet
        self.choices: dict[int, str] = {}
        self.finished = False
        self.lock = asyncio.Lock()
        self.message = None
        for choice in OPTIONS:
            self.add_item(ChoiceButton(choice))

    async def choose(self, interaction: discord.Interaction, choice: str):
        if interaction.user.id not in (self.challenger.id, self.opponent.id):
            return await interaction.response.send_message("You are not part of this duel.", ephemeral=True)
        async with self.lock:
            if self.finished:
                return await interaction.response.send_message("This duel has already ended.", ephemeral=True)
            if interaction.user.id in self.choices:
                return await interaction.response.send_message("You have already chosen and cannot change your choice.", ephemeral=True)

            self.choices[interaction.user.id] = choice
            await interaction.response.send_message("Your choice has been saved privately.", ephemeral=True)

            if len(self.choices) == 1:
                return

            self.finished = True
            first = self.choices[self.challenger.id]
            second = self.choices[self.opponent.id]
            result = 0 if first == second else 1 if WIN_CONDITIONS[first] == second else 2
            if result == 0:
                updateUser(self.challenger.id, int(getUser(self.challenger.id)["balance"]) + self.bet)
                updateUser(self.opponent.id, int(getUser(self.opponent.id)["balance"]) + self.bet)
                outcome = "Draw! Both bets have been refunded."
            else:
                winner = self.challenger if result == 1 else self.opponent
                updateUser(winner.id, int(getUser(winner.id)["balance"]) + self.bet * 2)
                outcome = f"Winner: {winner.mention}. Prize: **{self.bet * 2}** bolivars."

            embed = discord.Embed(
                title="Duel Results",
                description=(f"{self.challenger.mention}: {OPTIONS[first]} {first}\n"
                             f"{self.opponent.mention}: {OPTIONS[second]} {second}\n\n{outcome}"),
                color=discord.Color.green() if result else discord.Color.blue(),
            )
            if self.message:
                await self.message.edit(embed=embed, view=None)
            self.stop()

    async def on_timeout(self):
        async with self.lock:
            if self.finished:
                return
            self.finished = True
            updateUser(self.challenger.id, int(getUser(self.challenger.id)["balance"]) + self.bet)
            updateUser(self.opponent.id, int(getUser(self.opponent.id)["balance"]) + self.bet)
            if self.message:
                try:
                    await self.message.edit(
                        embed=discord.Embed(title="Duel Expired", description="Both players did not choose in time. All bets have been refunded."),
                        view=None,
                    )
                except discord.HTTPException:
                    pass
            self.stop()


class PPTInvitation(discord.ui.View):
    def __init__(self, challenger: discord.Member, opponent: discord.Member, bet: int):
        super().__init__(timeout=120)
        self.challenger = challenger
        self.opponent = opponent
        self.bet = bet
        self.finished = False
        self.lock = asyncio.Lock()
        self.message = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            return await interaction.response.send_message("Only the challenged player can accept.", ephemeral=True)
        async with self.lock:
            if self.finished:
                return await interaction.response.send_message("This invitation is no longer available.", ephemeral=True)
            if int(getUser(self.challenger.id)["balance"]) < self.bet or int(getUser(self.opponent.id)["balance"]) < self.bet:
                self.finished = True
                await interaction.response.edit_message(content="Challenge canceled: one of the players has insufficient balance.", embed=None, view=None)
                self.stop()
                return

            updateUser(self.challenger.id, int(getUser(self.challenger.id)["balance"]) - self.bet)
            updateUser(self.opponent.id, int(getUser(self.opponent.id)["balance"]) - self.bet)
            duel = PPTDuel(self.challenger, self.opponent, self.bet)
            embed = discord.Embed(
                title="Rock, Paper, Scissors — Duel",
                description=(
                    f"{self.challenger.mention}: Waiting for choice\n"
                    f"{self.opponent.mention}: Waiting for choice\n\n"
                    f"Bet: **{self.bet}** each (prize pool: **{2 * self.bet}**).\n"
                    "Choices stay hidden until both playplayersers have selected."
                ),
                color=discord.Color.blue(),
            )
            try:
                await interaction.response.edit_message(content=None, embed=embed, view=duel)
            except discord.HTTPException:
                updateUser(self.challenger.id, int(getUser(self.challenger.id)["balance"]) + self.bet)
                updateUser(self.opponent.id, int(getUser(self.opponent.id)["balance"]) + self.bet)
                self.finished = True
                self.stop()
                raise
            duel.message = interaction.message
            self.finished = True
            self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            return await interaction.response.send_message("Only the challenged player can decline.", ephemeral=True)
        async with self.lock:
            if self.finished:
                return await interaction.response.send_message("This invitation is no longer available.", ephemeral=True)
            self.finished = True
            await interaction.response.edit_message(content=f"{self.opponent.mention} declined the challenge.", embed=None, view=None)
            self.stop()

    async def on_timeout(self):
        async with self.lock:
            if self.finished:
                return
            self.finished = True
            if self.message:
                try:
                    await self.message.edit(content="The challenge invitation has expired.", embed=None, view=None)
                except discord.HTTPException:
                    pass
            self.stop()


#========================================================================================================================================


async def ppt(ctx, *args: str):
    if len(args) not in (1, 2):
        return await ctx.send("Usage: `*ppt <amount|allin>` or `*ppt @user <amount|allin>`")

    opponent = None
    if len(args) == 2:
        try:
            opponent = await commands.MemberConverter().convert(ctx, args[0])
        except commands.BadArgument:
            return await ctx.send("User not found. Try mentioning them.")
        if opponent.id == ctx.author.id or opponent.bot:
            return await ctx.send("You must challenge another human player.")

    balance = int(getUser(ctx.author.id)["balance"])
    try:
        bet = balance if args[-1].lower() == "allin" else int(args[-1])
    except ValueError:
        return await ctx.send("Enter a number or 'allin'.")
    if bet < 1:
        return await ctx.send("You must bet at least 1 bolivar.")
    if bet > balance:
        return await ctx.send("You do not have enough balance.")

    if opponent is None:
        updateUser(ctx.author.id, balance - bet)
        view = PPT(ctx.author.id, bet)
        embed = discord.Embed(title="Rock, Paper, Scissors", description="Choose an option.", color=discord.Color.blue())
        try:
            view.message = await ctx.send(embed=embed, view=view)
        except discord.HTTPException:
            updateUser(ctx.author.id, int(getUser(ctx.author.id)["balance"]) + bet)
            raise
        return

    invitation = PPTInvitation(ctx.author, opponent, bet)
    invitation.message = await ctx.send(
        content=f"{opponent.mention}, {ctx.author.mention} challenges you to Rock, Paper, Scissors for **{bet}** bolivars each.",
        view=invitation,
    )