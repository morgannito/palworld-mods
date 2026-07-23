"""PIDF Elite — les forces de l'ordre passent en mode SWAT : HP, attaque et
défense x3 pour toutes les unités de police (patrouilles, tours, boss).

Le complément naturel de GTAPalpagos : des primes x20 qui se méritent.
"""
from palmod import get, rows, set_

PAK_NAME = "PIDFElite"
TABLES = [
    "Pal/Content/Pal/DataTable/Character/DT_PalHumanParameter",
    "Pal/Content/Pal/DataTable/Character/DT_PalHumanParameter_Common",
]

MULT = 3
STATS = ("HP", "MeleeAttack", "ShotAttack", "Defense")


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        touched = 0
        for r in rows(a):
            if "Police" not in r["Name"]:
                continue
            for stat in STATS:
                try:
                    v = int(get(r, stat))
                except (TypeError, ValueError):
                    continue
                if v > 0:
                    set_(a, r, stat, v * MULT)
            touched += 1
        if touched == 0:
            raise RuntimeError("aucune row Police trouvée")


def verify(assets):
    a = assets[TABLES[0]]
    r = next(x for x in rows(a) if x["Name"] == "Police_Rifle")
    got = int(get(r, "HP"))
    return [] if got == 300 else [f"Police_Rifle HP = {got}, attendu 300"]
