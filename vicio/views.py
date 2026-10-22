import discord
from discord.ui import Button, View

from vicio.gacha import Character

from .bosses import bosses


class PaginatedView(View):
    def __init__(self, items: list[Character], timeout: int = 90):
        super().__init__(timeout=timeout)
        self.data = items
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= len(self.data) - 1

    def get_embed(self) -> tuple[discord.Embed, discord.File]:
        raise NotImplementedError("Las subclases deben implementar get_embed()")

    async def _update_view(self, interaction: discord.Interaction):
        self.update_buttons()
        embed, file = self.get_embed()
        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        await self._update_view(interaction)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        await self._update_view(interaction)


class InventoryView(PaginatedView):
    def get_embed(self) -> tuple[discord.Embed, discord.File]:
        character = self.data[self.current_page]
        file = discord.File(character.image, filename="char.webp")

        embed = discord.Embed(
            title=f"🎒 Inventory: {character.name}",
            description=character.desc,
            color=discord.Color.gold(),
        )
        embed.add_field(name="Rarity", value=character.rarity)
        embed.add_field(name="Sell Value", value=str(character.getSellValue()))
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        assert character.stats is not None
        for stat, valor in character.stats.items():
            embed.add_field(name=stat, value=str(valor), inline=True)
        embed.add_field(name="LVL", value=str(character.level))

        embed.set_image(url="attachment://char.webp")
        embed.set_footer(text=f"Page {self.current_page + 1} out of {len(self.data)}")
        return embed, file


class BossListView(PaginatedView):
    def __init__(self, data=None):
        boss_chars = [Character(boss_dict) for boss_dict in bosses]
        super().__init__(items=boss_chars)

    def get_embed(self) -> tuple[discord.Embed, discord.File]:
        boss = self.data[self.current_page]
        file = discord.File(boss.image, filename="boss.webp")
        boss_id = self.current_page + 1

        embed = discord.Embed(
            title=f"👹 Boss Arena: {boss.name}",
            description=boss.desc,
            color=discord.Color.dark_red(),
        )
        embed.add_field(name="Difficulty", value=boss.rarity)
        embed.add_field(name="Boss ID", value=f"#{boss_id}")
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        assert boss.stats is not None
        for stat, valor in boss.stats.items():
            embed.add_field(name=stat, value=str(valor), inline=True)
        embed.add_field(name="LVL", value=str(boss.level))

        embed.set_image(url="attachment://boss.webp")
        embed.set_footer(
            text=f"Boss {boss_id} out of {len(self.data)} | Use *boss fight {boss_id} to challenge!"
        )
        return embed, file
