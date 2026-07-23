"""Hordes massives — effectifs des outbreaks x3 (cap 30/vague pour la charge serveur), niveaux +3.

NB : la fréquence d'apparition des incidents n'est pas exposée en datatable
(DT_IncidentParameter est vide, la cadence vit dans le code) — on rend donc
chaque horde mémorable au lieu de les rendre plus fréquentes.
"""
from palmod import get, rows, set_

PAK_NAME = "MassiveOutbreaks"

_BASE = "Pal/Content/Pal/DataTable/Incident/RandomIncident_OutBreak/DT_RandomIncidentMonster_"
# Uniquement les hordes par biome (schéma Num/LevelMin/LevelMax).
# Les tables `outbreak_*` minuscules (ColorfulBird, QueenBee...) sont des
# événements scriptés à spawns individuels — schéma différent, on n'y touche pas.
_TABLES_SUFFIX = [
    "Outbreak_Desert", "Outbreak_Forest", "Outbreak_Forest_Frost",
    "Outbreak_Grass", "Outbreak_Grass2", "Outbreak_Grass_Desert",
    "Outbreak_Sakurajima", "Outbreak_Snow", "Outbreak_Volcano",
]
TABLES = [_BASE + s for s in _TABLES_SUFFIX]

NUM_MULT = 3
NUM_CAP = 30
LEVEL_BONUS = 3


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            num = int(get(r, "Num"))
            if num > 0:
                set_(a, r, "Num", min(NUM_CAP, num * NUM_MULT))
            set_(a, r, "LevelMin", int(get(r, "LevelMin")) + LEVEL_BONUS)
            set_(a, r, "LevelMax", int(get(r, "LevelMax")) + LEVEL_BONUS)
