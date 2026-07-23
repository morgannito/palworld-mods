"""Transporteurs rapides — TransportSpeed x2 pour tous les pals.

Réponse datatable à LA plainte n°1 des forums : les pals qui trottinent
pendant des heures avec une planche sous le bras. On ne touche ni WalkSpeed
ni RunSpeed (utilisés par les pals sauvages) : uniquement la vitesse en
mode transport, quasi exclusive au travail de base.
"""
from palmod import get, rows, set_

PAK_NAME = "FastHaulers"
TABLES = [
    "Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter",
    "Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter_Common",
]

MULT = 2


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            speed = get(r, "TransportSpeed")
            try:
                speed = int(speed)
            except (TypeError, ValueError):
                continue
            if speed > 0:
                set_(a, r, "TransportSpeed", speed * MULT)
