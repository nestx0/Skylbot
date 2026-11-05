import datetime

from database.dataBase import getUser, updateUser
from database.plantsDatabase import PlantsDatabase
from plants.plantObjects import Inventario, Planta, Semilla
from plants.plantShop import tienda
from plants.plantViews import PlantInventoryView, PlantShopView


async def shop(ctx):
    tienda.check_refresh()
    view = PlantShopView(shop=tienda)
    embed, file = view.get_embed()

    # Si en algún momento get_embed devuelve un archivo (imagen), lo manejamos
    kwargs = {"embed": embed, "view": view}
    if file:
        kwargs["file"] = file

    return await ctx.send(**kwargs)


async def plantinv(ctx):
    userID = ctx.author.id

    rawInv = PlantsDatabase.getInventory(userID)
    inv = Inventario()
    inv.load(rawInv)

    if not inv.inventory:
        return await ctx.send(
            "🌱 Your plant inventory is empty! Use the shop command to buy seeds."
        )

    view = PlantInventoryView(items=inv.inventory)
    embed, file = view.get_embed()

    kwargs = {"embed": embed, "view": view}
    if file:
        kwargs["file"] = file

    return await ctx.send(**kwargs)


async def water(ctx, pos: int | None = None):
    if pos is None:
        return await ctx.send("Syntax: `water <slot>` (Example: `water 1`)")

    userID = ctx.author.id
    actualPos = pos - 1

    rawInv = PlantsDatabase.getInventory(userID)
    inv = Inventario()
    inv.load(rawInv)

    if actualPos < 0 or actualPos >= len(inv.inventory):
        return await ctx.send(
            f"Invalid position. Choose between 1 and {len(inv.inventory)}."
        )

    item = inv.inventory[actualPos]

    if isinstance(item, Semilla):
        planta_nueva = item.germinar()
        inv.inventory[actualPos] = planta_nueva
        PlantsDatabase.updateInventory(user_id=userID, inventory_list=inv.toDict())

        return await ctx.send(
            f"🌱 Your seed bloomed into a **{planta_nueva.nombre}**! Check it in your `*plantinv`."
        )

    elif isinstance(item, Planta):
        hoy = datetime.date.today()

        if item.lastTimeWater == hoy:
            return await ctx.send(
                "💧 You have already watered this plant today. Come back tomorrow!"
            )

        if item.grow():
            inv.inventory[actualPos] = item
            PlantsDatabase.updateInventory(user_id=userID, inventory_list=inv.toDict())
            return await ctx.send(
                f"✨ You watered **{item.nombre}**! It leveled up to **Lvl {item.lvl}** (Value: 🪙 {item.value:,})."
            )
        else:
            return await ctx.send(
                "🏆 This plant has already reached its maximum value (🪙 500,000)!"
            )


async def sellplant(ctx, pos: int | None = None):
    if pos is None:
        return await ctx.send("Syntax: `sell <slot>` (Example: `sell 1`)")

    userID = ctx.author.id
    actualPos = pos - 1

    rawInv = PlantsDatabase.getInventory(userID)
    inv = Inventario()
    inv.load(rawInv)

    if actualPos < 0 or actualPos >= len(inv.inventory):
        return await ctx.send(
            f"Invalid position. Choose between 1 and {len(inv.inventory)}."
        )

    item = inv.inventory[actualPos]
    if isinstance(item, Semilla):
        return await ctx.send("You cannot sell a seed, water it first")

    elif isinstance(item, Planta):
        value = item.value
        balance = getUser(userID)["balance"]
        balance += value
        updateUser(userID, balance)
        inv.inventory.pop(actualPos)
        PlantsDatabase.updateInventory(userID, inv.toDict())
        return await ctx.send(
            f"Done! You sold your **{item.nombre}** for **{value:,}** bolivares. "
            f"Your new balance is **{balance:,}**."
        )
