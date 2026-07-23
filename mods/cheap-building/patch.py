"""Construction pas chère et flexible — matériaux des 498 constructions ÷5,
conso d'énergie des machines ÷2, et seuil de connexion des pièces x2.5
(la tolérance de snap responsable des erreurs « not connected to structure »,
plainte récurrente des forums)."""
from palmod import get, rows, set_

PAK_NAME = "CheapBuilding"
TABLES = [
    "Pal/Content/Pal/DataTable/MapObject/Building/DT_BuildObjectDataTable",
    "Pal/Content/Pal/DataTable/MapObject/Building/DT_BuildObjectDataTable_Common",
]

MATERIAL_DIV = 5
MATERIAL_SLOTS = 4
ENERGY_DIV = 2
NEIGHBOR_MULT = 2.5


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
                conso = None  # "+0" : pas de conso, on ne touche pas
            if conso and conso > 0:
                set_(a, r, "ConsumeEnergySpeed", conso / ENERGY_DIV)

            thr = get(r, "InstallNeighborThreshold")
            try:
                thr = float(thr)
            except (TypeError, ValueError):
                continue
            if thr > 0:
                set_(a, r, "InstallNeighborThreshold", thr * NEIGHBOR_MULT)