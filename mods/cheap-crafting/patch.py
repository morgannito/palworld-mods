"""Craft pas cher — coûts de matériaux et temps de travail divisés par 5 sur toutes les recettes."""
from palmod import get, rows, set_

PAK_NAME = "CheapCrafting"
TABLES = [
    "Pal/Content/Pal/DataTable/Item/DT_ItemRecipeDataTable",
    "Pal/Content/Pal/DataTable/Item/DT_ItemRecipeDataTable_Common",
]

DIV = 5
MATERIAL_SLOTS = 5


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            for n in range(1, MATERIAL_SLOTS + 1):
                count = int(get(r, f"Material{n}_Count"))
                if count > 0:
                    set_(a, r, f"Material{n}_Count", max(1, count // DIV))
            work = float(get(r, "WorkAmount"))
            if work > 0:
                set_(a, r, "WorkAmount", max(1.0, work / DIV))
