"""Tower Titans — les 21 boss de tours (Zoe, Lily, Axel…) passent de x40 à
x80 de HP : des sièges marathon à préparer en équipe, dans l'esprit
d'EpicBosses (qui les épargnait exprès). Dégâts inchangés.
"""
from palmod import get, rows, set_

PAK_NAME = "TowerTitans"
TABLES = [
    "Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter",
    "Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter_Common",
]

MULT = 2.0


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        touched = 0
        for r in rows(a):
            if not r["Name"].startswith("GYM_"):
                continue
            try:
                rate = float(get(r, "EnemyMaxHPRate"))
            except (TypeError, ValueError):
                continue
            if rate > 0:
                set_(a, r, "EnemyMaxHPRate", rate * MULT)
                touched += 1
        if touched == 0:
            raise RuntimeError("aucune row GYM_ trouvée")


def verify(assets):
    # les rates vanilla varient par boss (12 à 405) : on vérifie deux points connus
    a = assets[TABLES[0]]
    expected = {"GYM_ElecPanda": 24.0, "GYM_WorldTreeDragon": 80.0}
    fails = []
    for name, want in expected.items():
        r = next(x for x in rows(a) if x["Name"] == name)
        got = float(get(r, "EnemyMaxHPRate"))
        if got != want:
            fails.append(f"{name} EnemyMaxHPRate = {got}, attendu {want}")
    return fails
