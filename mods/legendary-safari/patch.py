"""Legendary Safari — l'île céleste (skyisland, lv 68-69) devient une réserve
de légendaires sauvages : les 46 spawners Common tirent dans un pool de 8
légendaires (choix déterministe par spawner). Boss de zone épargnés.

L'inverse philosophique de DepressoWorld : la zone endgame devient le terrain
de chasse ultime. Niveaux et effectifs vanilla.
"""
import hashlib

from palmod import enum_short, get, rows, set_

PAK_NAME = "LegendarySafari"
TABLES = ["Pal/Content/Pal/DataTable/Spawner/DT_PalWildSpawner"]

ZONE_PREFIX = "skyisland"
PAL_SLOTS = 3
# IDs internes validés contre DT_PalMonsterParameter 1.0
LEGENDARIES = [
    "JetDragon", "IceHorse", "BlackCentaur", "SaintCentaur",
    "NightLady", "MoonQueen", "Horus", "GoldenHorse",
]


def _pick(key):
    h = int(hashlib.sha1(key.encode()).hexdigest(), 16)
    return LEGENDARIES[h % len(LEGENDARIES)]


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
                set_(a, r, f"Pal_{n}", _pick(f"{r['Name']}/{n}"))
        touched += 1
    if touched == 0:
        raise RuntimeError("aucun spawner skyisland Common trouvé")


def verify(assets):
    a = assets[TABLES[0]]
    pals = set()
    for r in rows(a):
        if not r["Name"].startswith(ZONE_PREFIX):
            continue
        if enum_short(get(r, "SpawnerType")) != "Common":
            continue
        for n in range(1, PAL_SLOTS + 1):
            pal = str(get(r, f"Pal_{n}"))
            if pal not in ("None", "") and not pal.startswith("BOSS_"):
                pals.add(pal)
    bad = pals - set(LEGENDARIES)
    fails = []
    if bad:
        fails.append(f"pals non légendaires restants dans la zone : {sorted(bad)[:5]}")
    if len(pals) < 4:
        fails.append(f"diversité du pool trop faible : {sorted(pals)}")
    return fails
