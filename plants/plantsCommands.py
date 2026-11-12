import datetime

from command_utils import parse_positions
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


async def water(ctx, *, pos: str | None = None):
    if not pos:
        return await ctx.send(
            "Syntax: `water <slot ... | all | max>` (Example: `water 1 3` or `water all`)"
        )

    userID = ctx.author.id
    rawInv = PlantsDatabase.getInventory(userID)
    inv = Inventario()
    inv.load(rawInv)

    if not inv.inventory:
        return await ctx.send("Your inventory is empty.")

    try:
        positions, _ = parse_positions(pos, len(inv.inventory))
    except ValueError as exc:
        return await ctx.send(str(exc))

    indices_a_procesar = [position - 1 for position in positions]

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


async def sellplant(ctx, *, pos: str | None = None):
    if not pos:
        return await ctx.send(
            "Syntax: `sellplant <slot ... | all | max>` (Example: `sellplant 1 3` or `sellplant all`)"
        )

    userID = ctx.author.id
    rawInv = PlantsDatabase.getInventory(userID)
    inv = Inventario()
    inv.load(rawInv)

    if not inv.inventory:
        return await ctx.send("Your inventory is empty.")

    try:
        positions, all_selected = parse_positions(pos, len(inv.inventory))
    except ValueError as exc:
        return await ctx.send(str(exc))

    if all_selected:
        # Leave seeds in the inventory: they cannot be sold.
        positions = [p for p in positions if isinstance(inv.inventory[p - 1], Planta)]
    elif any(isinstance(inv.inventory[p - 1], Semilla) for p in positions):
        return await ctx.send("You cannot sell a seed, water it first")

    if not positions:
        return await ctx.send("You have no grown plants to sell.")

    selected = [inv.inventory[p - 1] for p in positions]
    value = sum(item.value for item in selected)
    for p in reversed(positions):
        inv.inventory.pop(p - 1)

    balance = getUser(userID)["balance"] + value
    updateUser(userID, balance)
    PlantsDatabase.updateInventory(userID, inv.toDict())
    names = ", ".join(item.nombre for item in selected)
    msg = (
        f"Done! You sold **{names}** for **{value:,}** bolivares. "
        f"Your new balance is **{balance:,}**."
    )
    if len(msg) > 1900:
        msg = (
            f"Done! You sold **{len(selected)}** plants for **{value:,}** bolivares. "
            f"Your new balance is **{balance:,}**."
        )
    return await ctx.send(msg)
