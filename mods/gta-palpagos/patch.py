"""GTA Palpagos — primes de crime x20 : chaque délit vaut très cher aux yeux des PIDF."""
from palmod import get, rows, set_

PAK_NAME = "GTAPalpagos"
TABLES = ["Pal/Content/Pal/DataTable/WorldSecurity/DT_WorldSecurity_CrimeMasterDataTable"]

MULT = 20


def patch(assets, extra):
    a = assets[TABLES[0]]
    for r in rows(a):
        set_(a, r, "BaseReward", int(get(r, "BaseReward")) * MULT)
