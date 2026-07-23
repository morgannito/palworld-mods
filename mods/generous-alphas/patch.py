"""Alphas généreux — chaque boss alpha droppe une schematic légendaire garantie + quantités doublées."""
import hashlib

from palmod import get, rows, set_

PAK_NAME = "GenerousAlphas"
TABLES = [
    "Pal/Content/Pal/DataTable/Character/DT_PalDropItem",
    "Pal/Content/Pal/DataTable/Character/DT_PalDropItem_Common",
]
EXTRA = ["Pal/Content/Pal/DataTable/Item/DT_ItemLotteryDataTable"]

SLOT_COUNT = 10


def _legendaries(lottery):
    bps = sorted({
        str(get(r, "StaticItemId"))
        for r in rows(lottery)
        if str(get(r, "StaticItemId")).startswith("Blueprint_")
        and str(get(r, "StaticItemId")).endswith("_5")
    })
    if not bps:
        raise RuntimeError("aucune schematic légendaire trouvée dans la loterie")
    return bps


def _pick(bps, key):
    h = int(hashlib.sha1(key.encode()).hexdigest(), 16)
    return bps[h % len(bps)]


def patch(assets, extra):
    bps = _legendaries(extra[EXTRA[0]])

    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            cid = str(get(r, "CharacterID"))
            if not cid.upper().startswith("BOSS_"):
                continue

            free = None
            for n in range(1, SLOT_COUNT + 1):
                if str(get(r, f"ItemId{n}")) in ("None", ""):
                    free = free or n
                else:
                    set_(a, r, f"Max{n}", int(get(r, f"Max{n}")) * 2)

            if free is not None:
                set_(a, r, f"ItemId{free}", _pick(bps, cid))
                set_(a, r, f"Rate{free}", 100.0)
                set_(a, r, f"min{free}", 1)
                set_(a, r, f"Max{free}", 1)
