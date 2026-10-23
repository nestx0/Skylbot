import copy
import random
import discord

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
        # Eventos Aleatorios de Turno
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

        # Evasión
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
                    final_dmg = defender.stats["HP"]  # Daño letal garantizado
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
                    extra_dmg = max(
                        1, round(final_dmg * 0.5)
                    )  # El golpe extra hace la mitad de daño
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


#====================================================================================================


async def combat(ctx, option: int | None = None, rival: discord.Member | None = None):
    if not option:
        return await ctx.send(
            "You have to choose who you are using in your fight, type *fight <fighter (inventory position)> <rival>"
        )
    if not rival:
        return await ctx.send(
            "No rival chosen, type *fight <fighter (inventory position)> <rival>"
        )

    userID = ctx.author.id
    userInventory = getInventory(userID)
    rivalInventory = getInventory(rival.id)

    if userInventory == []:
        return await ctx.send("You don't even have someone to fight with...")

    if rivalInventory == []:
        return await ctx.send("Your opponent hasn't even someone to defend them...")

    if len(userInventory) < option - 1:
        return await ctx.send("You don't even have that many characters...")

    userChar = userInventory[option - 1]
    rivalChar = rivalInventory[0]

    resumen, winner = fight(userChar, rivalChar)
    if len(resumen) > 1990:
        await ctx.send(resumen[:1990] + "...")
        await ctx.send("..." + resumen[1990:])
    else:
        await ctx.send(resumen)
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