"""Pêche miraculeuse — poissons Boss ×4 et Nushi (légendaires) ×10 dans la loterie de pêche."""
from palmod import get, rows, set_

PAK_NAME = "MiracleFishing"
TABLES = ["Pal/Content/Pal/DataTable/Fishing/DT_PalFishingSpotLotteryDataTable"]

BOSS_MULT = 4.0
NUSHI_MULT = 10.0


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        shadow = str(get(r, "FishShadowId"))
        mult = None
        if shadow.endswith("_Nushi"):
            mult = NUSHI_MULT
        elif shadow.endswith("_Boss"):
            mult = BOSS_MULT
        if mult:
            set_(a, r, "Weight", float(get(r, "Weight")) * mult)
