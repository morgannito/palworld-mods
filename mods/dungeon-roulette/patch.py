"""Dungeon Roulette — les 160 boss de donjons sont rebrassés : chaque donjon
peut sortir N'IMPORTE LEQUEL des 149 boss du jeu (choix déterministe par
spawner), au niveau local du donjon. Fini le boss prévisible de la zone —
un donjon de plaine peut cacher un Astegon.

Les niveaux (LvMin/LvMax) et effectifs restent vanilla : la surprise vient
de l'espèce, pas d'un one-shot.
"""
import hashlib

from palmod import enum_short, get, rows, set_

PAK_NAME = "DungeonRoulette"
TABLES = ["Pal/Content/Pal/DataTable/Spawner/DT_PalWildSpawner"]


def patch(assets, extra):
    a = assets[TABLES[0]]
    spawners = [
        r for r in rows(a)
        if enum_short(get(r, "SpawnerType")) == "RandomDungeonBoss"
    ]
    if not spawners:
        raise RuntimeError("aucun spawner RandomDungeonBoss")

    pool = sorted({
        str(get(r, "Pal_1")) for r in spawners
        if str(get(r, "Pal_1")).startswith("BOSS_")
    })
    for r in spawners:
        h = int(hashlib.sha1(r["Name"].encode()).hexdigest(), 16)
        set_(a, r, "Pal_1", pool[h % len(pool)])


def verify(assets):
    a = assets[TABLES[0]]
    spawners = [
        r for r in rows(a)
        if enum_short(get(r, "SpawnerType")) == "RandomDungeonBoss"
    ]
    bad = [r["Name"] for r in spawners if not str(get(r, "Pal_1")).startswith("BOSS_")]
    distinct = {str(get(r, "Pal_1")) for r in spawners}
    fails = []
    if bad:
        fails.append(f"spawners sans boss : {bad[:3]}")
    if len(distinct) < 50:
        fails.append(f"diversité trop faible après remix : {len(distinct)}")
    return fails
