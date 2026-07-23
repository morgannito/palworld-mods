"""Statues généreuses — moitié moins de reliques par rang de Statue de Pouvoir.

Combo naturel avec BoostedRelics (reliques x4 en drop) : la boucle
« explorer → ramasser → améliorer » tourne 8x plus vite qu'en vanilla.
"""
from palmod import get, rows, set_

PAK_NAME = "CheapStatues"
TABLES = ["Pal/Content/Pal/DataTable/Player/DT_PlayerStatusRankMasterDataTable"]

DIV = 2


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        req = int(get(r, "RequiredRelicNum"))
        if req > 1:
            set_(a, r, "RequiredRelicNum", max(1, req // DIV))
