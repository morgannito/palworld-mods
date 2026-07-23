"""Dungeon Deluxe — les coffres de fin de donjon haut grade (Grade_02)
apparaissent 4x plus souvent dans la loterie des salles de récompense.
"""
from palmod import get, rows, set_

PAK_NAME = "DungeonDeluxe"
TABLES = ["Pal/Content/Pal/DataTable/Dungeon/DT_DungeonRewardSpawnerLotteryDataTable"]

MULT = 4.0


def patch(assets, extra):
    a = assets[TABLES[0]]
    touched = 0
    for r in rows(a):
        if "Grade_02" not in str(get(r, "LotteryValue")):
            continue
        set_(a, r, "Weight", float(get(r, "Weight")) * MULT)
        touched += 1
    if touched == 0:
        raise RuntimeError("aucun coffre Grade_02 trouvé")
