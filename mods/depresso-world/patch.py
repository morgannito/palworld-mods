"""Depresso World — la zone de départ (spawners green_*) ne fait plus
apparaître QUE des Depresso. Niveaux et effectifs vanilla, boss épargnés.

Zéro utilité. 100 % meme. Vos potes s'en souviendront.
"""
from palmod import enum_short, get, rows, set_

PAK_NAME = "DepressoWorld"
TABLES = ["Pal/Content/Pal/DataTable/Spawner/DT_PalWildSpawner"]

DEPRESSO = "NegativeOctopus"
ZONE_PREFIX = "green_"
PAL_SLOTS = 3


def patch(assets, extra):
    a = assets[TABLES[0]]
    touched = 0
    for r in rows(a):
        if not r["Name"].startswith(ZONE_PREFIX):
            continue
        if enum_short(get(r, "SpawnerType")) != "Common":
            continue
        for n in range(1, PAL_SLOTS + 1):
            pal = str(get(r, f"Pal_{n}"))
            if pal not in ("None", "") and not pal.startswith("BOSS_"):
                set_(a, r, f"Pal_{n}", DEPRESSO)
        touched += 1
    if touched == 0:
        raise RuntimeError("aucun spawner green_* Common trouvé")
