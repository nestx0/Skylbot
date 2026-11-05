import random

import discord

from plants.plantObjects import Semilla
from plants.plantShop import PlantShop
from vicio.views import PaginatedView

flowers = ["💐", "🌸", "💮", "🪷", "🏵️", "🌹", "🥀", "🌺", "🌻", "🌼", "🌷", "🪻"]


class PlantInventoryView(PaginatedView):
    def get_embed(self) -> tuple[discord.Embed, discord.File | None]:
        item = self.data[self.current_page]
        florDeTurno = random.choice(flowers)
        embed = discord.Embed(
            title=f"🎒 Inventory: {item.nombre}",
            color=discord.Color.green(),
        )
        embed.add_field(name="Name", value=item.nombre, inline=True)
        embed.add_field(name="Rarity", value=item.rarity, inline=True)

        if item.esSemilla:
            embed.add_field(name="Status", value="🌱 Seed (Ungerminated)", inline=True)
            embed.add_field(
                name="Action", value="Use `*water` to germinate", inline=False
            )
        else:
            embed.add_field(name="Level", value=f"Lvl {item.lvl}", inline=True)
            embed.add_field(
                name="Streak", value=f"{florDeTurno} {item.racha} days", inline=True
            )
            embed.add_field(name="Sell Value", value=f"🪙 {item.value:,}", inline=True)

        embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.data)}")

        return embed, None


class PlantShopView(PaginatedView):
    def __init__(self, shop: PlantShop, timeout: int = 90):
        self.shop = shop
        super().__init__(items=shop.shop, timeout=timeout)

    def get_embed(self) -> tuple[discord.Embed, discord.File | None]:
        if not self.data:
            embed = discord.Embed(
                title="Shop Empty",
                description="All daily seeds have been bought! Come back tomorrow.",
                color=discord.Color.red(),
            )
            return embed, None

        item: Semilla = self.data[self.current_page]

        embed = discord.Embed(
            title=f"Seed Shop: {item.nombre}", color=discord.Color.green()
        )
        embed.add_field(name="Item", value=item.nombre, inline=True)
        embed.add_field(name="Rarity", value=item.rarity, inline=True)
        embed.add_field(
            name="Price",
            value=f"🪙 {self.shop.prices[self.current_page]}",
            inline=False,
        )
        embed.set_footer(text=f"Offer {self.current_page + 1} of {len(self.data)}")

        return embed, None

    @discord.ui.button(
        label="Buy Seed", style=discord.ButtonStyle.success, emoji="🛒", row=0
    )
    async def buy_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        success, message = self.shop.buy(
            pos=self.current_page + 1, userID=interaction.user.id
        )

        if not success:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
            return

        await interaction.response.send_message(f"✅ {message}", ephemeral=True)

        if self.current_page >= len(self.data) and self.current_page > 0:
            self.current_page -= 1

        if not self.data:
            button.disabled = True

        self.update_buttons()
        embed, file = self.get_embed()
        assert interaction.message is not None
        await interaction.message.edit(embed=embed, view=self)
