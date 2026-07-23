"""Pond Deluxe — la mare à poissons sort 4x plus souvent ses pals rares
(les entrées à poids < 1, dont les variantes dragons et espèces exotiques).
"""
from palmod import get, rows, set_

PAK_NAME = "PondDeluxe"
TABLES = ["Pal/Content/Pal/DataTable/Fishing/DT_PalFishPondLotteryDataTable"]

RARE_THRESHOLD = 1.0
MULT = 4.0


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        w = float(get(r, "Weight"))
        if 0 < w < RARE_THRESHOLD:
            set_(a, r, "Weight", round(w * MULT, 2))
