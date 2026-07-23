"""Night Terrors — la nuit, le monde change : ~1 spawner sur 4 gagne une
variante nocturne peuplée de pals _Dark (Baphomet_Dark, IceHorse_Dark,
NightLady_Dark…), +8 niveaux. Dormir devient une stratégie, sortir la nuit
un choix assumé — et le seul moyen de capturer certaines terreurs.

Mécanique éprouvée : le jeu utilise déjà OnlyTime::Night sur 229 spawners
vanilla. Les donjons (pas de cycle jour/nuit) sont exclus, les spawners de
boss aussi.
"""
import hashlib

from palmod import clone_row, enum_short, get, rows, set_

PAK_NAME = "NightTerrors"
TABLES = ["Pal/Content/Pal/DataTable/Spawner/DT_PalWildSpawner"]
EXTRA = ["Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter"]

CLONE_RATIO = 4          # 1 spawner Common sur 4 gagne une variante nocturne
LEVEL_BONUS = 8
LEVEL_CAP = 65
WEIGHT_MULT = 0.6        # présence nocturne sensible mais pas envahissante
PAL_SLOTS = 3


def _dark_pool(params):
    pool = sorted(
        r["Name"] for r in rows(params)
        if r["Name"].endswith("_Dark")
        and not r["Name"].startswith(("BOSS_", "RAID_", "SUMMON_", "PREDATOR_"))
    )
    if len(pool) < 8:
        raise RuntimeError(f"pool _Dark trop maigre : {pool}")
    return pool


def _pick(pool, key):
    h = int(hashlib.sha1(key.encode()).hexdigest(), 16)
    return pool[h % len(pool)]


def patch(assets, extra):
    a = assets[TABLES[0]]
    pool = _dark_pool(extra[EXTRA[0]])
    data = rows(a)

    candidates = [
        r for r in data
        if enum_short(get(r, "SpawnerType")) == "Common"
        and enum_short(get(r, "OnlyTime")) == "Undefined"
        and not r["Name"].startswith("dungeon")
    ]
    clones = []
    for i, r in enumerate(candidates):
        if i % CLONE_RATIO:
            continue
        r2 = clone_row(a, r, f"{r['Name']}_nightterror")
        set_(a, r2, "OnlyTime", "EPalOneDayTimeType::Night")
        set_(a, r2, "Weight", max(10.0, float(get(r, "Weight")) * WEIGHT_MULT))
        for n in range(1, PAL_SLOTS + 1):
            pal = str(get(r2, f"Pal_{n}"))
            if pal in ("None", "") or pal.startswith("BOSS_"):
                continue
            set_(a, r2, f"Pal_{n}", _pick(pool, f"{r['Name']}/{n}"))
            lv_min = int(get(r2, f"LvMin_{n}"))
            lv_max = int(get(r2, f"LvMax_{n}"))
            set_(a, r2, f"LvMin_{n}", min(LEVEL_CAP, lv_min + LEVEL_BONUS))
            set_(a, r2, f"LvMax_{n}", min(LEVEL_CAP, max(lv_max + LEVEL_BONUS, lv_min + LEVEL_BONUS)))
        clones.append(r2)
    if not clones:
        raise RuntimeError("aucun clone nocturne créé")
    data.extend(clones)


def verify(assets):
    a = assets[TABLES[0]]
    night = [r for r in rows(a) if r["Name"].endswith("_nightterror")]
    fails = []
    if len(night) < 100:
        fails.append(f"seulement {len(night)} spawners nocturnes créés")
    bad_time = [r["Name"] for r in night if enum_short(get(r, "OnlyTime")) != "Night"]
    if bad_time:
        fails.append(f"clones sans OnlyTime::Night : {bad_time[:3]}")
    pals = set()
    for r in night:
        for n in range(1, PAL_SLOTS + 1):
            p = str(get(r, f"Pal_{n}"))
            if p not in ("None", ""):
                pals.add(p)
    non_dark = {p for p in pals if not p.endswith("_Dark") and not p.startswith("BOSS_")}
    if non_dark:
        fails.append(f"pals non-dark dans les clones : {sorted(non_dark)[:4]}")
    return fails
