"""Construction pas chère — matériaux des 498 constructions ÷5, conso d'énergie des machines ÷2."""
from palmod import get, rows, set_

PAK_NAME = "CheapBuilding"
TABLES = [
    "Pal/Content/Pal/DataTable/MapObject/Building/DT_BuildObjectDataTable",
    "Pal/Content/Pal/DataTable/MapObject/Building/DT_BuildObjectDataTable_Common",
]

MATERIAL_DIV = 5
MATERIAL_SLOTS = 4
ENERGY_DIV = 2


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            for n in range(1, MATERIAL_SLOTS + 1):
                count = int(get(r, f"Material{n}_Count"))
                if count > 0:
                    set_(a, r, f"Material{n}_Count", max(1, count // MATERIAL_DIV))
            conso = get(r, "ConsumeEnergySpeed")
            try:
                conso = float(conso)
            except (TypeError, ValueError):
                continue  # "+0" : pas de conso, on ne touche pas
            if conso > 0:
                set_(a, r, "ConsumeEnergySpeed", conso / ENERGY_DIV)