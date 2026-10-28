import asyncio
import copy
import random

import discord
from discord.ext import commands

from database.dataBase import getUser, updateUser
from juegos.ppt import PPTInvitation

from .gacha import Character, getInventory, saveInventory


def fight(char1: Character, char2: Character):
    p1 = copy.deepcopy(char1)
    p2 = copy.deepcopy(char2)
    resumen = ""

    assert p1.stats is not None
    assert p2.stats is not None
    p1_max_hp, p2_max_hp = p1.stats["HP"], p2.stats["HP"]
    p1_init = p1.stats["SPE"] * random.uniform(0.9, 1.1)
    p2_init = p2.stats["SPE"] * random.uniform(0.9, 1.1)

    if p2_init > p1_init:
        attacker, defender = p2, p1
        atk_max_hp, def_max_hp = p2_max_hp, p1_max_hp
    else:
        attacker, defender = p1, p2
        atk_max_hp, def_max_hp = p1_max_hp, p2_max_hp

    resumen += f"⚔️ **{attacker.name}** vs **{defender.name}**!\n"
    resumen += f"💨 **{attacker.name}** is faster and takes the first strike.\n\n"

    turno = 1
    frenzy_multiplier = 1.0
    winner_name = None

    while p1.stats["HP"] > 0 and p2.stats["HP"] > 0:
        assert attacker.stats is not None
        assert defender.stats is not None
        if random.randint(1, 100) <= 5:
            if attacker.stats["LCK"] > defender.stats["LCK"]:
                heal = int(atk_max_hp * 0.15)
                attacker.stats["HP"] = min(atk_max_hp, attacker.stats["HP"] + heal)
                resumen += f"🍀 **LUCKY DROP!** {attacker.name} recovered {heal} HP!\n"
            else:
                dmg = int(defender.stats["HP"] * 0.10)
                defender.stats["HP"] = max(0, defender.stats["HP"] - dmg)
                resumen += f"⚡ **ARENA HAZARD!** A stray lightning hit {defender.name} for {dmg} damage!\n"

        dodge_chance = min(
            25.0,
            (defender.stats["SPE"] / max(1, attacker.stats["SPE"])) * 5
            + (defender.stats["LCK"] / 20),
        )

        if random.uniform(0, 100) < dodge_chance:
            resumen += (
                f"🛡️ **Turn {turno}:** {defender.name} gracefully dodged the attack!\n"
            )
        else:
            base_dmg = (attacker.stats["ATK"] ** 2) / max(
                1, attacker.stats["ATK"] + defender.stats["DEF"]
            )
            varianza = random.uniform(0.85, 1.15)

            is_desperate = attacker.stats["HP"] <= (atk_max_hp * 0.20)
            desperation_mult = 1.5 if is_desperate else 1.0

            prob_critico = min(50.0, attacker.stats["LCK"] / 10.0)
            es_critico = random.uniform(0, 100) < prob_critico
            multiplicador_crit = 1.5 if es_critico else 1.0

            final_dmg = max(
                1,
                round(
                    base_dmg
                    * varianza
                    * multiplicador_crit
                    * desperation_mult
                    * frenzy_multiplier
                ),
            )

            prob_bloqueo = min(20.0, defender.stats["DEF"] / 100.0)
            bloqueo_texto = ""
            if random.uniform(0, 100) < prob_bloqueo:
                final_dmg = round(final_dmg * 0.2)
                bloqueo_texto = " **(PERFECT GUARD! 🛡️)**"

            ejecucion_texto = ""
            if 0 < defender.stats["HP"] < (def_max_hp * 0.15):
                prob_ejecucion = min(25.0, attacker.stats["LCK"] / 50.0)
                if random.uniform(0, 100) < prob_ejecucion:
                    final_dmg = defender.stats["HP"]
                    ejecucion_texto = " **(FATAL EXECUTION! ☠️)**"

            defender.stats["HP"] = max(0, defender.stats["HP"] - final_dmg)

            crit_text = (
                " **(CRITICAL HIT! 💥)**" if es_critico and not ejecucion_texto else ""
            )
            desp_text = " **(DESPERATION! 💢)**" if is_desperate else ""

            resumen += f"🥊 **Turn {turno}:** {attacker.name} deals {final_dmg} damage!{crit_text}{desp_text}{bloqueo_texto}{ejecucion_texto} ({defender.name} HP: {defender.stats['HP']})\n"

            if defender.stats["HP"] > 0:
                diferencia_velocidad = attacker.stats["SPE"] / max(
                    1, defender.stats["SPE"]
                )
                if diferencia_velocidad > 1.5 and random.uniform(0, 100) < 30.0:
                    extra_dmg = max(1, round(final_dmg * 0.5))
                    defender.stats["HP"] = max(0, defender.stats["HP"] - extra_dmg)
                    resumen += f"🌪️ **SPEED BURST!** {attacker.name} is too fast and lands an extra hit for {extra_dmg} damage! ({defender.name} HP: {defender.stats['HP']})\n"

        if defender.stats["HP"] <= 0:
            resumen += f"\n🏆 **FIGHT OVER! {attacker.name} stands victorious!**"
            winner_name = attacker.name
            break

        attacker, defender = defender, attacker
        atk_max_hp, def_max_hp = def_max_hp, atk_max_hp
        turno += 1
        frenzy_multiplier += 0.3

        if turno == 10:
            resumen += "\n🔥 **SUDDEN DEATH! ALL DAMAGE IS MASSIVELY INCREASED!** 🔥\n"

        if turno > 20:
            resumen += "\n⏳ **Time Limit Reached! It's a DRAW!**"
            break

    return resumen, winner_name


# ====================================================================================================


class CombatPickButton(discord.ui.Button):
    def __init__(self, label: str, index: int):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        await self.view.pick(interaction, self.index)


class CombatPickView(discord.ui.View):
    def __init__(
        self,
        challenger: discord.Member,
        opponent: discord.Member,
        challenger_char,
        bet: int,
        invitation_message: discord.Message,
    ):
        super().__init__(timeout=120)
        self.challenger = challenger
        self.opponent = opponent
        self.challenger_char = challenger_char
        self.bet = bet
        self.invitation_message = invitation_message
        self.opponent_char = None
        self.finished = False
        self.lock = asyncio.Lock()
        self.add_items()

    def add_items(self):
        inventory = getInventory(self.opponent.id)
        for i, char in enumerate(inventory):
            label = f"{i + 1}. {char.name} [{char.rarity}]"
            if len(label) > 80:
                label = label[:77] + "..."
            self.add_item(CombatPickButton(label, i))

    async def pick(self, interaction: discord.Interaction, index: int):
        if interaction.user.id != self.opponent.id:
            return await interaction.response.send_message(
                "Only the challenged player can choose their character.", ephemeral=True
            )
        async with self.lock:
            if self.finished:
                return await interaction.response.send_message(
                    "This selection has already ended.", ephemeral=True
                )
            inventory = getInventory(self.opponent.id)
            if index < 0 or index >= len(inventory):
                return await interaction.response.send_message(
                    "Invalid character selection.", ephemeral=True
                )
            self.opponent_char = inventory[index]
            self.finished = True

        resumen, winner_name = fight(self.challenger_char, self.opponent_char)
        if winner_name == self.challenger_char.name:
            updateUser(
                self.challenger.id,
                int(getUser(self.challenger.id)["balance"]) + self.bet * 2,
            )
            outcome = f"Winner: {self.challenger.mention}. Prize: **{self.bet * 2}** bolivars."
            color = discord.Color.green()
        elif winner_name == self.opponent_char.name:
            updateUser(
                self.opponent.id,
                int(getUser(self.opponent.id)["balance"]) + self.bet * 2,
            )
            outcome = (
                f"Winner: {self.opponent.mention}. Prize: **{self.bet * 2}** bolivars."
            )
            color = discord.Color.green()
        else:
            updateUser(
                self.challenger.id,
                int(getUser(self.challenger.id)["balance"]) + self.bet,
            )
            updateUser(
                self.opponent.id, int(getUser(self.opponent.id)["balance"]) + self.bet
            )
            outcome = "Draw! Both bets have been refunded."
            color = discord.Color.blue()

        embed = discord.Embed(
            title="Combat Results",
            description=(
                f"{self.challenger.mention} ({self.challenger_char.name}) vs {self.opponent.mention} ({self.opponent_char.name})\n\n"
                f"{outcome}\n\n{resumen}"
            ),
            color=color,
        )
        assert embed.description is not None
        if len(embed.description) > 4096:
            embed.description = embed.description[:4093] + "..."
        try:
            await interaction.response.edit_message(
                content=None, embed=embed, view=None
            )
        except discord.HTTPException:
            try:
                await self.invitation_message.edit(content=None, embed=embed, view=None)
            except discord.HTTPException:
                pass
        self.stop()

    async def on_timeout(self):
        async with self.lock:
            if self.finished:
                return
            self.finished = True
        try:
            updateUser(
                self.challenger.id,
                int(getUser(self.challenger.id)["balance"]) + self.bet,
            )
            updateUser(
                self.opponent.id, int(getUser(self.opponent.id)["balance"]) + self.bet
            )
        except Exception:
            pass
        try:
            await self.invitation_message.edit(
                content="Combat selection expired. Both bets have been refunded.",
                embed=None,
                view=None,
            )
        except discord.HTTPException:
            pass
        self.stop()


class CombatInvitation(PPTInvitation):
    message: discord.Message | None

    def __init__(
        self,
        challenger: discord.Member,
        opponent: discord.Member,
        challenger_char,
        bet: int,
    ):
        super().__init__(challenger, opponent, bet)
        self.challenger_char = challenger_char

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            return await interaction.response.send_message(
                "Only the challenged player can accept.", ephemeral=True
            )
        async with self.lock:
            if self.finished:
                return await interaction.response.send_message(
                    "This invitation is no longer available.", ephemeral=True
                )
            challenger_balance = int(getUser(self.challenger.id)["balance"])
            opponent_balance = int(getUser(self.opponent.id)["balance"])
            if challenger_balance < self.bet or opponent_balance < self.bet:
                self.finished = True
                await interaction.response.edit_message(
                    content="Challenge canceled: one of the players has insufficient balance.",
                    embed=None,
                    view=None,
                )
                self.stop()
                return
            updateUser(self.challenger.id, challenger_balance - self.bet)
            updateUser(self.opponent.id, opponent_balance - self.bet)

        opponent_inventory = getInventory(self.opponent.id)
        if not opponent_inventory:
            try:
                updateUser(
                    self.challenger.id,
                    int(getUser(self.challenger.id)["balance"]) + self.bet,
                )
                updateUser(
                    self.opponent.id,
                    int(getUser(self.opponent.id)["balance"]) + self.bet,
                )
            except Exception:
                pass
            self.finished = True
            await interaction.response.edit_message(
                content="Challenge canceled: the opponent has no characters.",
                embed=None,
                view=None,
            )
            self.stop()
            return

        assert interaction.message is not None
        pick_view = CombatPickView(
            self.challenger,
            self.opponent,
            self.challenger_char,
            self.bet,
            interaction.message,
        )
        embed = discord.Embed(
            title="Combat - Choose your character",
            description=(
                f"{self.opponent.mention}, choose which character from your inventory you will use.\n\n"
                f"{self.challenger.mention} chose: **{self.challenger_char.name}** [{self.challenger_char.rarity}]\n"
                f"Bet: **{self.bet}** each (prize pool: **{self.bet * 2}**)"
            ),
            color=discord.Color.blue(),
        )
        try:
            await interaction.response.edit_message(
                content=None, embed=embed, view=pick_view
            )
        except discord.HTTPException:
            try:
                updateUser(
                    self.challenger.id,
                    int(getUser(self.challenger.id)["balance"]) + self.bet,
                )
                updateUser(
                    self.opponent.id,
                    int(getUser(self.opponent.id)["balance"]) + self.bet,
                )
            except Exception:
                pass
            self.finished = True
            self.stop()
            raise
        pick_view.invitation_message = interaction.message
        self.finished = True
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent.id:
            return await interaction.response.send_message(
                "Only the challenged player can decline.", ephemeral=True
            )
        async with self.lock:
            if self.finished:
                return await interaction.response.send_message(
                    "This invitation is no longer available.", ephemeral=True
                )
            self.finished = True
            await interaction.response.edit_message(
                content=f"{self.opponent.mention} declined the challenge.",
                embed=None,
                view=None,
            )
            self.stop()

    async def on_timeout(self):
        async with self.lock:
            if self.finished:
                return
            self.finished = True
            if self.message:
                try:
                    await self.message.edit(
                        content="The combat challenge has expired.",
                        embed=None,
                        view=None,
                    )
                except discord.HTTPException:
                    pass
            self.stop()


async def combat(ctx, *args: str):
    if len(args) != 3:
        return await ctx.send(
            "Usage: `*combat @rival <amount|allin> <your_character_position>`"
        )

    try:
        rival = await commands.MemberConverter().convert(ctx, args[0])
    except commands.BadArgument:
        return await ctx.send("User not found. Try mentioning them.")

    if rival.id == ctx.author.id or rival.bot:
        return await ctx.send("You must challenge another human player.")

    userID = ctx.author.id
    userInventory = getInventory(userID)
    if not userInventory:
        return await ctx.send("You don't even have someone to fight with...")

    try:
        char_pos = int(args[2])
    except ValueError:
        return await ctx.send("Character position must be a number.")

    if char_pos < 1 or char_pos > len(userInventory):
        return await ctx.send("You have to select a valid position")

    challenger_char = userInventory[char_pos - 1]
    balance = int(getUser(userID)["balance"])
    try:
        bet = balance if args[1].lower() == "allin" else int(args[1])
    except ValueError:
        return await ctx.send("Enter a number or 'allin'.")
    if bet < 1:
        return await ctx.send("You must bet at least 1 bolivar.")
    if bet > balance:
        return await ctx.send("You do not have enough balance.")

    invitation = CombatInvitation(ctx.author, rival, challenger_char, bet)
    invitation.message = await ctx.send(
        content=f"{rival.mention}, {ctx.author.mention} challenges you to a combat for **{bet}** bolivars each using **{challenger_char.name}**.",
        view=invitation,
    )
    return


async def setDefender(ctx, option: int | None = None):

    if option == None:
        return await ctx.send(
            "If you wanna set a defender up you have to type *setDefender <position in your inventory>"
        )

    userID = ctx.author.id
    inventory = getInventory(userID)

    if int(option) <= 0 or int(option) > len(inventory):
        return await ctx.send("You have to select a valid position")

    charDef = inventory[option - 1]
    aux = inventory[0]
    inventory[0] = charDef
    inventory[option - 1] = aux

    saveInventory(userID, inventory)

    return await ctx.send(f"Your defender is now {charDef.name}")
