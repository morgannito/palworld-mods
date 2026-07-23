"""Pure Passives — les passifs perdent leurs malus (les valeurs d'effet
négatives passent à 0) : « Musclehead » donne +30 % d'attaque sans le
-50 % de vitesse de craft, « Brave » reste intact, etc.

On ne touche ni aux bonus ni aux poids de loterie : la rareté des bons
passifs reste vanilla, ils cessent juste d'être des pièges.
"""
from palmod import get, rows, set_

PAK_NAME = "PurePassives"
TABLES = [
    "Pal/Content/Pal/DataTable/PassiveSkill/DT_PassiveSkill_Main",
    "Pal/Content/Pal/DataTable/PassiveSkill/DT_PassiveSkill_Main_Common",
]

EFFECT_SLOTS = 4


def patch(assets, extra):
    for table in TABLES:
        a = assets[table]
        for r in rows(a):
            for n in range(1, EFFECT_SLOTS + 1):
                try:
                    v = float(get(r, f"EffectValue{n}"))
                except (TypeError, ValueError):
                    continue  # "+0" : slot inutilisé
                if v < 0:
                    set_(a, r, f"EffectValue{n}", 0.0)
