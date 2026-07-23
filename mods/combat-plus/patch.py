"""Combat Plus — des combats plus nerveux et plus variés :

- cooldowns de toutes les attaques -40 % (le vrai changement de rythme)
- les attaques faibles (0 < Power < 125, médiane vanilla 250) frappent +30 %
  pour élargir le pool viable — les utilitaires à Power 0 restent intactes
"""
from palmod import get, rows, set_

PAK_NAME = "CombatPlus"
TABLES = [
    "Pal/Content/Pal/DataTable/Waza/DT_WazaDataTable",
    "Pal/Content/Pal/DataTable/Waza/DT_WazaDataTable_Common",
]

COOLTIME_MULT = 0.6
WEAK_THRESHOLD = 125
WEAK_MULT = 1.3


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            try:
                ct = float(get(r, "CoolTime"))
            except (TypeError, ValueError):
                ct = None
            if ct and ct > 0:
                set_(a, r, "CoolTime", round(ct * COOLTIME_MULT, 2))

            power = int(get(r, "Power"))
            if 0 < power < WEAK_THRESHOLD:
                boosted = int(power * WEAK_MULT)
                set_(a, r, "Power", boosted)
                if int(get(r, "DisplayPower")) > 0:
                    set_(a, r, "DisplayPower", boosted)
