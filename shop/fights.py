import copy
import random


def fight(char1, char2):
    p1 = copy.deepcopy(char1)
    p2 = copy.deepcopy(char2)
    resumen = ""

    p1_max_hp = p1.stats["HP"]
    p2_max_hp = p2.stats["HP"]

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
    frenzy_multiplier = 1.0  # En lugar de *= 2, le sumaremos 0.3 cada turno

    while p1.stats["HP"] > 0 and p2.stats["HP"] > 0:
        if random.randint(1, 100) <= 5:
            if attacker.stats["LCK"] > defender.stats["LCK"]:
                heal = int(atk_max_hp * 0.15)
                attacker.stats["HP"] += heal
                resumen += f"🍀 **LUCKY DROP!** {attacker.name} found a health potion and recovered {heal} HP!\n"
            else:
                dmg = int(defender.stats["HP"] * 0.10)
                defender.stats["HP"] -= dmg
                resumen += f"⚡ **ARENA HAZARD!** A stray lightning hit {defender.name} for {dmg} damage!\n"

        dodge_chance = min(
            25.0,
            (defender.stats["SPE"] / attacker.stats["SPE"]) * 5
            + (defender.stats["LCK"] / 20),
        )

        if random.uniform(0, 100) < dodge_chance:
            resumen += (
                f"🛡️ **Turn {turno}:** {defender.name} gracefully dodged the attack!\n"
            )
        else:
            base_dmg = (100 * attacker.stats["ATK"]) / (100 + defender.stats["DEF"])
            varianza = random.uniform(0.85, 1.15)

            desperation_mult = 1.0
            is_desperate = False
            if attacker.stats["HP"] <= (atk_max_hp * 0.20):
                desperation_mult = 1.5
                is_desperate = True

            prob_critico = min(50.0, attacker.stats["LCK"] / 10.0)
            es_critico = random.uniform(0, 100) < prob_critico
            multiplicador_crit = 1.5 if es_critico else 1.0

            final_dmg = round(
                base_dmg
                * varianza
                * multiplicador_crit
                * desperation_mult
                * frenzy_multiplier
            )
            if final_dmg < 1:
                final_dmg = 1

            defender.stats["HP"] -= final_dmg
            if defender.stats["HP"] < 0:
                defender.stats["HP"] = 0

            crit_text = " **(CRITICAL HIT! 💥)**" if es_critico else ""
            desp_text = " **(DESPERATION STRIKE! 💢)**" if is_desperate else ""

            resumen += f"🥊 **Turn {turno}:** {attacker.name} deals {final_dmg} damage!{crit_text}{desp_text} ({defender.name} HP: {defender.stats['HP']})\n"

        if defender.stats["HP"] <= 0:
            resumen += f"\n🏆 **FIGHT OVER! {attacker.name} stands victorious!**"
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

    return resumen, attacker.name
