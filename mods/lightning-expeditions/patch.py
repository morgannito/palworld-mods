"""Expéditions éclair — durées ÷10, récompenses ×5 (loterie Expedition_*)."""
from palmod import get, rows, set_

PAK_NAME = "LightningExpeditions"
TABLES = [
    "Pal/Content/Pal/DataTable/CharacterTeamMission/DT_CharacterTeamMissionDataTable",
    "Pal/Content/Pal/DataTable/Item/DT_ItemLotteryDataTable",
]

TIME_DIV = 10
REWARD_MULT = 5


def patch(assets, extra):
    missions = assets[TABLES[0]]
    for r in rows(missions):
        secs = int(get(r, "RequiredSeconds"))
        set_(missions, r, "RequiredSeconds", max(60, secs // TIME_DIV))

    lottery = assets[TABLES[1]]
    for r in rows(lottery):
        if not str(get(r, "FieldName")).startswith("Expedition_"):
            continue
        set_(lottery, r, "MinNum", max(1, int(get(r, "MinNum")) * REWARD_MULT))
        set_(lottery, r, "MaxNum", max(1, int(get(r, "MaxNum")) * REWARD_MULT))
