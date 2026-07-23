"""Better Bases — la base de tes rêves, plus vite :

- progression : ouvriers x2 par niveau de palbox (cap 50 = BaseCampWorkerMaxNum
  de l'ini serveur), bases de guilde débloquées plus tôt (2 dès le lv5, 4 au lv15 ;
  cap 4 = BaseCampMaxNumInGuild de l'ini)
- santé : les pals ouvriers n'ont plus aucun malus de maladie et guérissent
  à 100 % au passage dans la palbox
- cultures : pousse ÷5, récolte x3, travail de semis/arrosage/récolte ÷5
- zen : les 8 pétages de plombs (sabotage, glandage, hikikomori, boulimie,
  bagarre...) ne se déclenchent plus (TriggerSanity 0) — Trantrum/Escape/
  OverworkDeath étaient déjà désactivés par le jeu
- machines : puits/carrière/scierie/mines produisent 5x plus vite
- skill fruits : l'arbre donne des fruits Rarity2 x2 et Rarity3 x3 plus souvent

NB : le rayon de la base n'est pas en datatable (BP/code, UE4SS only).
"""
from palmod import get, rows, set_

PAK_NAME = "BetterBases"
TABLES = [
    "Pal/Content/Pal/DataTable/BaseCamp/DT_BaseCampLevelData",
    "Pal/Content/Pal/DataTable/BaseCamp/DT_BaseCampWorkerSickDataTable",
    "Pal/Content/Pal/DataTable/MapObject/DT_MapObjectFarmCrop",
    "Pal/Content/Pal/DataTable/BaseCamp/DT_BaseCampWorkerEventDataTable",
    "Pal/Content/Pal/DataTable/MapObject/DT_MapObjectItemProductDataTable",
    "Pal/Content/Pal/DataTable/MapObject/DT_MapObjectItemProductDataTable_Common",
    "Pal/Content/Pal/DataTable/MapObject/DT_MapObjectFarmSkillFruitsLottery",
]

WORKER_MULT = 2
WORKER_CAP = 50          # doit rester <= BaseCampWorkerMaxNum de l'ini
GUILD_CAMPS = [(15, 4), (10, 3), (5, 2)]  # (niveau minimum, bases) — cap ini = 4
CROP_TIME_DIV = 5
CROP_YIELD_MULT = 3
CROP_WORK_DIV = 5
MACHINE_WORK_DIV = 5
FRUIT_RARITY_MULT = {"Rarity2": 2, "Rarity3": 3}


def patch(assets, extra):
    levels = assets[TABLES[0]]
    for r in rows(levels):
        lv = int(get(r, "Level"))
        workers = int(get(r, "WorkerMaxNum"))
        set_(levels, r, "WorkerMaxNum", min(WORKER_CAP, workers * WORKER_MULT))
        for min_lv, camps in GUILD_CAMPS:
            if lv >= min_lv:
                set_(levels, r, "BaseCampMaxNumInGuild",
                     max(int(get(r, "BaseCampMaxNumInGuild")), camps))
                break

    sick = assets[TABLES[1]]
    for r in rows(sick):
        set_(sick, r, "WorkSpeed", 0)
        set_(sick, r, "MoveSpeed", 0)
        set_(sick, r, "SatietyDecrease", 0)
        if int(get(r, "RecoveryProbabilityPercentageInPalBox")) > 0:
            set_(sick, r, "RecoveryProbabilityPercentageInPalBox", 100)

    crops = assets[TABLES[2]]
    for r in rows(crops):
        set_(crops, r, "GrowupTime", max(30.0, float(get(r, "GrowupTime")) / CROP_TIME_DIV))
        set_(crops, r, "CropItemNum", int(get(r, "CropItemNum")) * CROP_YIELD_MULT)
        for field in ("SeedingWorkAmount", "WateringWorkAmount", "HarvestWorkAmount"):
            set_(crops, r, field, max(100.0, float(get(r, field)) / CROP_WORK_DIV))

    events = assets[TABLES[3]]
    for r in rows(events):
        set_(events, r, "TriggerSanity", 0)

    for table in (TABLES[4], TABLES[5]):
        machines = assets[table]
        for r in rows(machines):
            work = get(r, "RequiredWorkAmount")
            try:
                work = float(work)
            except (TypeError, ValueError):
                continue
            set_(machines, r, "RequiredWorkAmount", max(50.0, work / MACHINE_WORK_DIV))

    fruits = assets[TABLES[6]]
    for r in rows(fruits):
        for suffix, mult in FRUIT_RARITY_MULT.items():
            if r["Name"].endswith(suffix):
                set_(fruits, r, "Weight", int(get(r, "Weight")) * mult)
