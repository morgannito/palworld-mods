"""Marchand de pals pimpé — les vendeurs de pals proposent aussi des légendaires haut niveau."""
import copy

from palmod import ensure_name, get, prop, rows, set_

PAK_NAME = "PalShopPimped"
TABLES = ["Pal/Content/Pal/DataTable/PalShop/DT_PalShopCreateData"]

# IDs internes validés contre DT_PalMonsterParameter 1.0
LEGENDARIES = [
    "JetDragon",      # Jetragon
    "IceHorse",       # Frostallion
    "BlackCentaur",   # Necromus
    "SaintCentaur",   # Paladius
    "NightLady",      # Bellanoir
    "MoonQueen",      # Selene
    "Horus",          # Faleris
    "GoldenHorse",    # Palomba dorée
]
MAX_LEVEL = 50


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        if r["Name"].startswith("Test_"):
            continue
        arr = prop(r, "CharacterIDArray")
        template = arr["Value"][0]
        existing = {e["Value"][0]["Value"] for e in arr["Value"]}
        for pal in LEGENDARIES:
            if pal in existing:
                continue
            elem = copy.deepcopy(template)
            elem["Value"][0]["Value"] = pal
            ensure_name(a, pal)
            arr["Value"].append(elem)
        set_(a, r, "CharacterNum", int(get(r, "CharacterNum")) + 1)
        set_(a, r, "MaxCharacterLevel", MAX_LEVEL)
