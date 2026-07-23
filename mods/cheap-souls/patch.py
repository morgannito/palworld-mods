"""Cheap Souls — l'amélioration des pals par pierres d'âme coûte moitié moins
sur les 20 rangs (et le reset d'or est symbolique). Combo avec BoostedRelics
et CheapStatues : toute la boucle d'enhancement respire.
"""
from palmod import get, rows, set_

PAK_NAME = "CheapSouls"
TABLES = ["Pal/Content/Pal/DataTable/Character/DT_CharacterUpgradeMasterDataTable"]

DIV = 2


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        num = int(get(r, "RequiredItemNum"))
        if num > 1:
            set_(a, r, "RequiredItemNum", max(1, num // DIV))
        money = int(get(r, "ResetRequiredMoney"))
        if money > 100:
            set_(a, r, "ResetRequiredMoney", max(100, money // DIV))


def verify(assets):
    a = assets[TABLES[0]]
    r = next(x for x in rows(a) if int(get(x, "Rank")) == 4)
    got = int(get(r, "RequiredItemNum"))
    return [] if got == 2 else [f"Rank 4 RequiredItemNum = {got}, attendu 2"]
