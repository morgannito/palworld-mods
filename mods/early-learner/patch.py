"""Early Learner — les pals apprennent leurs attaques 2x plus tôt
(5772 entrées PalID x attaque x niveau, divisées par 2).

Anubis a son Sand Tornado au lv8 au lieu du lv15 ; combiné au breeding
rapide, les rosters deviennent intéressants dès le midgame.
"""
from palmod import get, rows, set_

PAK_NAME = "EarlyLearner"
TABLES = [
    "Pal/Content/Pal/DataTable/Waza/DT_WazaMasterLevel",
    "Pal/Content/Pal/DataTable/Waza/DT_WazaMasterLevel_Common",
]

DIV = 2


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            lv = int(get(r, "Level"))
            if lv > 1:
                set_(a, r, "Level", max(1, lv // DIV))


def verify(assets):
    a = assets[TABLES[0]]
    row = next(r for r in rows(a) if r["Name"] == "Anubis015")
    got = int(get(row, "Level"))
    return [] if got == 7 else [f"Anubis015 Level = {got}, attendu 7"]
