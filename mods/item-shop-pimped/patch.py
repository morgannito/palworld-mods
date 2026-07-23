"""Marchands d'objets pimpés — les boutiques des villages vendent aussi du
premium à prix salés : sphères Tera, pierres d'amélioration IV, diamants,
clés de coffre or. L'or accumulé retrouve une utilité endgame.
"""
import copy

from palmod import ensure_name, prop, rows

PAK_NAME = "ItemShopPimped"
TABLES = ["Pal/Content/Pal/DataTable/ItemShop/DT_ItemShopCreateData_Common"]

# (item validé dans DT_ItemDataTable, prix imposé, quantité par achat)
PREMIUM = [
    ("PalSphere_Tera", 15000, 1),
    ("PalUpgradeStone4", 30000, 1),
    ("Diamond", 25000, 1),
    ("TreasureBoxKey02", 20000, 1),
]


def _set(struct_value, name, value):
    for p in struct_value:
        if p["Name"] == name:
            p["Value"] = value
            return
    raise KeyError(name)


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        if r["Name"].startswith("Test"):
            continue
        arr = prop(r, "productDataArray")
        template = arr["Value"][0]
        existing = {
            next(p["Value"] for p in e["Value"] if p["Name"] == "StaticItemID")
            for e in arr["Value"]
        }
        for item, price, num in PREMIUM:
            if item in existing:
                continue
            product = copy.deepcopy(template)
            _set(product["Value"], "StaticItemID", item)
            _set(product["Value"], "OverridePrice", price)
            _set(product["Value"], "ProductNum", num)
            _set(product["Value"], "Stock", 0)
            ensure_name(a, item)
            arr["Value"].append(product)
