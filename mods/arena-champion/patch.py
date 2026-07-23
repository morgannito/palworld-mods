"""Arena Champion — récompenses de l'arène solo x5 (premier clear et reclears).

L'arène 1.0 est sous-récompensée par rapport au temps investi : x5 la remet
au niveau des autres boucles endgame.
"""
from palmod import prop, rows

PAK_NAME = "ArenaChampion"
TABLES = ["Pal/Content/Pal/DataTable/Arena/DT_ArenaSoloRewardTable"]

MULT = 5


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        for field in ("FirstClearReward", "RepeatClearReward"):
            for reward in prop(r, field)["Value"]:
                for p in reward["Value"]:
                    if p["Name"] in ("Min", "Max") and int(p["Value"]) > 0:
                        p["Value"] = int(p["Value"]) * MULT
