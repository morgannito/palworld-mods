"""Coffres jackpot — chaque slot de coffre Grade2+ peut sortir une schematic légendaire (~2 %)."""
import hashlib

from palmod import clone_row, get, rows, set_

PAK_NAME = "JackpotChests"
TABLES = ["Pal/Content/Pal/DataTable/Item/DT_ItemLotteryDataTable"]

JACKPOT_SHARE = 0.02


def _pick(bps, key):
    h = int(hashlib.sha1(key.encode()).hexdigest(), 16)
    return bps[h % len(bps)]


def patch(assets, extra):
    a = assets[TABLES[0]]
    data = rows(a)

    bps = sorted({
        str(get(r, "StaticItemId"))
        for r in data
        if str(get(r, "StaticItemId")).startswith("Blueprint_")
        and str(get(r, "StaticItemId")).endswith("_5")
    })
    if not bps:
        raise RuntimeError("aucune schematic légendaire trouvée dans la loterie")

    slots = {}
    for r in data:
        grade = str(get(r, "TreasureBoxGrade"))
        if grade.endswith("Grade1") or grade.endswith("None"):
            continue
        key = (str(get(r, "FieldName")), get(r, "SlotNo"), grade)
        slots.setdefault(key, []).append(r)

    if not slots:
        raise RuntimeError("aucun slot de coffre Grade2+ trouvé")

    next_id = max(int(r["Name"]) for r in data) + 1
    for (field, slot_no, grade), slot_rows in sorted(slots.items()):
        total = sum(float(get(r, "WeightInSlot")) for r in slot_rows)
        r2 = clone_row(a, slot_rows[0], str(next_id))
        next_id += 1
        set_(a, r2, "StaticItemId", _pick(bps, f"{field}/{slot_no}/{grade}"))
        set_(a, r2, "WeightInSlot", max(1.0, round(total * JACKPOT_SHARE, 2)))
        set_(a, r2, "MinNum", 1)
        set_(a, r2, "MaxNum", 1)
        data.append(r2)
