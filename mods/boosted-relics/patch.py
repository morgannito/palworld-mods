"""Reliques boostées — les reliques de l'Arbre-Monde tombent 4x plus souvent (coffres et pals)."""
from palmod import get, rows, set_

PAK_NAME = "BoostedRelics"
TABLES = [
    "Pal/Content/Pal/DataTable/Item/DT_ItemLotteryDataTable",
    "Pal/Content/Pal/DataTable/Character/DT_PalDropItem",
    "Pal/Content/Pal/DataTable/Character/DT_PalDropItem_Common",
]

MULT = 4.0
SLOT_COUNT = 10


def _is_relic(item_id):
    return "Relic" in str(item_id)


def patch(assets, extra):
    lottery = assets[TABLES[0]]
    for r in rows(lottery):
        if _is_relic(get(r, "StaticItemId")):
            set_(lottery, r, "WeightInSlot", float(get(r, "WeightInSlot")) * MULT)

    for table in TABLES[1:]:
        a = assets[table]
        for r in rows(a):
            for n in range(1, SLOT_COUNT + 1):
                if not _is_relic(get(r, f"ItemId{n}")):
                    continue
                rate = get(r, f"Rate{n}")
                try:
                    rate = float(rate)
                except (TypeError, ValueError):
                    continue  # "+0" : slot lié au tirage du slot précédent, on n'y touche pas
                set_(a, r, f"Rate{n}", min(100.0, rate * MULT))
