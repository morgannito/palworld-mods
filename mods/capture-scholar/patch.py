"""Capture Scholar — bonus d'XP de capture x3 (les 10 premières captures
de chaque espèce). Capturer devient la vraie voie de leveling.
"""
from palmod import get, rows, set_

PAK_NAME = "CaptureScholar"
TABLES = ["Pal/Content/Pal/DataTable/Exp/DT_PalCaptureBonusExpTable"]

MULT = 3


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        exp = int(get(r, "BonusExp"))
        if exp > 0:
            set_(a, r, "BonusExp", exp * MULT)
