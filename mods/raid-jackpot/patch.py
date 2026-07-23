"""Raids jackpot — récompenses d'invasion de base ×10."""
from palmod import get, rows, set_

PAK_NAME = "RaidJackpot"
TABLES = ["Pal/Content/Pal/DataTable/Invader/DT_PalInvaderReward"]

MULT = 10


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        n = 1
        while True:
            try:
                mn = int(get(r, f"Min{n}"))
                mx = int(get(r, f"Max{n}"))
            except KeyError:
                break
            if mx > 0:
                set_(a, r, f"Min{n}", max(1, mn) * MULT)
                set_(a, r, f"Max{n}", mx * MULT)
            n += 1
