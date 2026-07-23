"""Progression fluide — le grind de la 1.0 raboté :

- labo : travail de recherche ÷5 (50k-200k+ par techno vanilla) et matériaux ÷5
- table d'opération : chirurgie des passifs ÷5 (jusqu'à 50 000 or vanilla)
- arbre de technologies : coût en points ÷2 (÷5 tuerait la progression)
"""
from palmod import get, rows, set_

PAK_NAME = "FastProgress"
TABLES = [
    "Pal/Content/Pal/DataTable/Lab/DT_LabResearchDataTable",
    "Pal/Content/Pal/DataTable/MapObject/DT_OperatingTablePassiveSkillDataTable",
    "Pal/Content/Pal/DataTable/Technology/DT_TechnologyRecipeUnlock",
    "Pal/Content/Pal/DataTable/Technology/DT_TechnologyRecipeUnlock_Common",
]

LAB_DIV = 5
LAB_MATERIAL_SLOTS = 4
SURGERY_DIV = 5
TECH_DIV = 2


def patch(assets, extra):
    lab = assets[TABLES[0]]
    for r in rows(lab):
        work = int(get(r, "RequiredWorkAmount"))
        if work > 0:
            set_(lab, r, "RequiredWorkAmount", max(100, work // LAB_DIV))
        for n in range(1, LAB_MATERIAL_SLOTS + 1):
            count = int(get(r, f"Material{n}_Count"))
            if count > 0:
                set_(lab, r, f"Material{n}_Count", max(1, count // LAB_DIV))

    surgery = assets[TABLES[1]]
    for r in rows(surgery):
        price = int(get(r, "Price"))
        if price > 0:
            set_(surgery, r, "Price", max(100, price // SURGERY_DIV))

    for table in (TABLES[2], TABLES[3]):
        tech = assets[table]
        for r in rows(tech):
            cost = int(get(r, "Cost"))
            if cost > 1:
                set_(tech, r, "Cost", max(1, cost // TECH_DIV))
