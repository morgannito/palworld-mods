"""Drops élémentaires — chaque pal droppe un item selon son élément (feu -> organe igné, dragon -> diamant...)."""
from palmod import enum_short, get, prop, rows, set_

PAK_NAME = "ElementalDrops"
TABLES = [
    "Pal/Content/Pal/DataTable/Character/DT_PalDropItem",
    "Pal/Content/Pal/DataTable/Character/DT_PalDropItem_Common",
]
EXTRA = ["Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter"]

# IDs validés contre DT_ItemDataTable 1.0
ELEMENT_ITEMS = {
    "Normal": "Leather",
    "Fire": "FireOrgan",
    "Water": "PalFluid",
    "Electricity": "ElectricOrgan",
    "Ice": "IceOrgan",
    "Leaf": "Honey",
    "Dark": "Venom",
    "Dragon": "Diamond",
    "Earth": "Ruby",
}
RATE = 80.0
MIN, MAX = 1, 3
SLOT_COUNT = 10


def _first_free_slot(row):
    for n in range(1, SLOT_COUNT + 1):
        if str(get(row, f"ItemId{n}")) in ("None", ""):
            return n
    return None


def patch(assets, extra):
    params = extra[EXTRA[0]]
    element_of = {
        r["Name"]: enum_short(get(r, "ElementType1")) for r in rows(params)
    }

    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            elem = element_of.get(str(get(r, "CharacterID")))
            item = ELEMENT_ITEMS.get(elem)
            if item is None:
                continue
            n = _first_free_slot(r)
            if n is None:
                continue
            set_(a, r, f"ItemId{n}", item)
            set_(a, r, f"Rate{n}", RATE)
            set_(a, r, f"min{n}", MIN)
            set_(a, r, f"Max{n}", MAX)
