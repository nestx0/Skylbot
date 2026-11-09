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


async def water(ctx, pos=None):
    if pos is None:
        return await ctx.send(
            "Syntax: `water <slot>` (Example: `water 1` or `water all`)"
        )

    userID = ctx.author.id
    rawInv = PlantsDatabase.getInventory(userID)
    inv = Inventario()
    inv.load(rawInv)

    if not inv.inventory:
        return await ctx.send("Your inventory is empty.")

    if str(pos).lower() == "all":
        indices_a_procesar = range(len(inv.inventory))
    else:
        try:
            actualPos = int(pos) - 1
        except ValueError:
            return await ctx.send("Invalid position. Please provide a number or 'all'.")

        if actualPos < 0 or actualPos >= len(inv.inventory):
            return await ctx.send(
                f"Invalid position. Choose between 1 and {len(inv.inventory)}."
            )

        indices_a_procesar = [actualPos]

    mensajes = []
    hoy = datetime.date.today()
    inventario_modificado = False

    for i in indices_a_procesar:
        item = inv.inventory[i]

        if isinstance(item, Planta):
            if item.lastTimeWater == hoy:
                mensajes.append(
                    f"💧 You have already watered **{item.nombre}** today. Come back tomorrow!"
                )
                continue  # Evita que la planta crezca si ya fue regada hoy

            if item.grow():
                inv.inventory[i] = item
                inventario_modificado = True
                mensajes.append(
                    f"✨ You watered **{item.nombre}**! It leveled up to **Lvl {item.lvl}** (Value: 🪙 {item.value:,})."
                )
            else:
                mensajes.append(
                    f"🏆 **{item.nombre}** has already reached its maximum value (🪙 250,000)!"
                )

        elif isinstance(item, Semilla):
            planta_nueva = item.germinar()
            inv.inventory[i] = planta_nueva
            inventario_modificado = True
            mensajes.append(
                f"🌱 Your seed bloomed into a **{planta_nueva.nombre}**! Check it in your `*plantinv`."
            )

    if inventario_modificado:
        PlantsDatabase.updateInventory(user_id=userID, inventory_list=inv.toDict())

    if mensajes:
        final_msg = "\n".join(mensajes)

        if len(final_msg) > 1950:
            final_msg = final_msg[:1950] + "\n... (Message truncated, too many plants!)"

        return await ctx.send(final_msg)
    else:
        return await ctx.send("No actions could be performed.")


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
