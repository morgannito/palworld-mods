"""Visiteurs fréquents — les PNJ ambulants (marchands...) visitent la base
dès le grade 1 au lieu du grade 7, et le marchand itinérant pèse x2 dans
la loterie des visites.
"""
from palmod import get, rows, set_

PAK_NAME = "FrequentVisitors"
TABLES = ["Pal/Content/Pal/DataTable/Invader/DT_PalVisitorNPC"]

SALES_WEIGHT_MULT = 2.0


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        try:
            w = float(get(r, "Weight"))
        except (TypeError, ValueError):
            continue  # "+0" : entrées désactivées, on n'y touche pas
        if w <= 0:
            continue
        if int(get(r, "InvadeGradeMin")) > 1:
            set_(a, r, "InvadeGradeMin", 1)
        if "SalesPerson" in r["Name"]:
            set_(a, r, "Weight", w * SALES_WEIGHT_MULT)


def verify(assets):
    a = assets[TABLES[0]]
    r = next(x for x in rows(a) if x["Name"] == "SalesPerson")
    fails = []
    if int(get(r, "InvadeGradeMin")) != 1:
        fails.append(f"SalesPerson InvadeGradeMin = {get(r, 'InvadeGradeMin')}, attendu 1")
    if float(get(r, "Weight")) != 2.0:
        fails.append(f"SalesPerson Weight = {get(r, 'Weight')}, attendu 2.0")
    return fails
