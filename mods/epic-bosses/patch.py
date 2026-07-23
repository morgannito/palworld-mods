"""Epic Bosses — les 322 boss (alphas, tours, donjons) ont 4x plus de HP.

Des vrais fights coop de 10-15 minutes au lieu de 90 secondes. Dégâts
inchangés : plus long, pas plus punitif. Les raid bosses déjà gonflés
(EnemyMaxHPRate 42x/50x, type Bellanoir) sont épargnés. EnemyMaxHPRate ne
s'applique qu'aux ennemis : les boss capturés gardent leurs stats normales.
"""
from palmod import get, rows, set_

PAK_NAME = "EpicBosses"
TABLES = [
    "Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter",
    "Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter_Common",
]

MULT = 4.0
ALREADY_RAID_THRESHOLD = 5.0


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            if not r["Name"].startswith("BOSS_"):
                continue
            try:
                rate = float(get(r, "EnemyMaxHPRate"))
            except (TypeError, ValueError):
                continue
            if 0 < rate < ALREADY_RAID_THRESHOLD:
                set_(a, r, "EnemyMaxHPRate", round(rate * MULT, 4))


def verify(assets):
    a = assets[TABLES[0]]
    fails = []
    alpaca_boss = next(r for r in rows(a) if r["Name"] == "BOSS_Alpaca")
    if float(get(alpaca_boss, "EnemyMaxHPRate")) != 4.0:
        fails.append(f"BOSS_Alpaca EnemyMaxHPRate = {get(alpaca_boss, 'EnemyMaxHPRate')}, attendu 4.0")
    raid = [r for r in rows(a) if r["Name"].startswith("BOSS_")
            and float(get(r, "EnemyMaxHPRate")) >= 42.0]
    if not raid:
        fails.append("les raid bosses (rate >= 42) ont été multipliés — ils devaient être épargnés")
    return fails
