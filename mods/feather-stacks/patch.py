"""Feather Stacks — tous les items 2x plus légers, piles doublées.

L'équivalent server-side du mod client n°2 de Nexus (Carry Weight ~250K DL) :
au lieu de booster le poids portable du joueur (stat côté client), on allège
les objets eux-mêmes — même effet, appliqué à tout le monde via le serveur.
Les équipements non empilables (stack 1) le restent.
"""
from palmod import get, rows, set_

PAK_NAME = "FeatherStacks"
TABLES = [
    "Pal/Content/Pal/DataTable/Item/DT_ItemDataTable",
    "Pal/Content/Pal/DataTable/Item/DT_ItemDataTable_Common",
]

WEIGHT_MULT = 0.5
STACK_MULT = 2
STACK_CAP = 9999


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            try:
                w = float(get(r, "Weight"))
            except (TypeError, ValueError):
                w = None
            if w and w > 0:
                set_(a, r, "Weight", round(w * WEIGHT_MULT, 2))

            stack = int(get(r, "MaxStackCount"))
            if 1 < stack < STACK_CAP:
                set_(a, r, "MaxStackCount", min(STACK_CAP, stack * STACK_MULT))
