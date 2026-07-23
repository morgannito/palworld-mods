"""Bases XXL — rayon de base 35 m -> 70 m, via le CDO de BP_PalGameSetting.

Réplique maison du principe du mod Nexus #3983 (pak pur, server-side, Linux OK),
avec les finitions que la version du commerce oublie :
- SpawnerDisableDistance relevé (sinon les pals sauvages spawnent DANS la base
  agrandie)
- point de départ des raids repoussé (sinon les invasions commencent à
  l'intérieur du nouveau rayon)
- rayon d'aspiration des objets par les transporteurs x2 (bonus logistique)

Sans le pak côté client, le cercle bleu affiché reste à 35 m mais le rayon
FONCTIONNEL est bien 70 m (comportement documenté du mod de référence).
"""
from palmod import bp_prop

PAK_NAME = "BiggerBases"
TABLES = ["Pal/Content/Pal/Blueprint/System/BP_PalGameSetting"]

RADIUS_MULT = 2.0


def patch(assets, extra):
    a = assets[TABLES[0]]

    for name, value in [
        ("BaseCampAreaRange", 3500.0 * RADIUS_MULT),          # 70 m
        ("BaseCampExtraWorkAreaRange", 7000.0 * RADIUS_MULT),
        ("SpawnerDisableDistanceCM_FromBaseCamp", 8500.0),    # > nouveau rayon
        ("InvadeStartPoint_BaseCampRadius_Min_cm", 8000),     # raids hors base
    ]:
        bp_prop(a, name)["Value"] = value

    absorb = bp_prop(a, "TransportItemAbsorbRangeByWorkSuitabilityRank")
    for elem in absorb["Value"]:
        try:
            v = float(elem["Value"])
        except (TypeError, ValueError):
            continue  # "+0" : rangs sans aspiration, inchangés
        if v > 0:
            elem["Value"] = v * 2


def verify(assets):
    got = float(bp_prop(assets[TABLES[0]], "BaseCampAreaRange")["Value"])
    return [] if got == 3500.0 * RADIUS_MULT else [f"BaseCampAreaRange = {got}, attendu {3500.0 * RADIUS_MULT}"]
