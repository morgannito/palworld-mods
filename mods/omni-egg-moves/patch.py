"""Omni Egg Moves — les 8 attaques héritables les plus puissantes du jeu
deviennent transmissibles par œuf à TOUTES les espèces.

Le pool est calculé dynamiquement : parmi les attaques déjà présentes dans la
table d'héritage (donc héritables par design), on prend le top 8 en puissance
— en excluant les signatures (Unique_*) et SelfExplosion (grief). Combo
évident avec le breeding rapide : la chasse au parent parfait devient un vrai
jeu dans le jeu.
"""
from palmod import clone_row, enum_short, get, rows, set_

PAK_NAME = "OmniEggMoves"
TABLES = ["Pal/Content/Pal/DataTable/Waza/DT_WazaMasterTamago"]
EXTRA = ["Pal/Content/Pal/DataTable/Waza/DT_WazaDataTable"]

POOL_SIZE = 8
EXCLUDE_PREFIXES = ("Unique_",)
EXCLUDE = {"SelfExplosion"}


def _top_moves(waza_table, inheritable):
    powers = {}
    for r in rows(waza_table):
        wid = enum_short(get(r, "WazaType"))
        try:
            powers[wid] = int(get(r, "Power"))
        except (TypeError, ValueError):
            continue
    ranked = sorted(
        (w for w in inheritable
         if w in powers and w not in EXCLUDE
         and not w.startswith(EXCLUDE_PREFIXES)),
        key=lambda w: -powers[w],
    )
    return ranked[:POOL_SIZE]


def patch(assets, extra):
    a = assets[TABLES[0]]
    data = rows(a)

    have = {(str(get(r, "PalID")), enum_short(get(r, "WazaID"))) for r in data}
    inheritable = {w for _, w in have}
    pool = _top_moves(extra[EXTRA[0]], inheritable)
    if len(pool) < POOL_SIZE:
        raise RuntimeError(f"pool incomplet : {pool}")

    pals = sorted({p for p, _ in have})
    next_id = max(int(r["Name"]) for r in data) + 1
    template = data[0]
    for pal in pals:
        for move in pool:
            if (pal, move) in have:
                continue
            r2 = clone_row(a, template, str(next_id))
            next_id += 1
            set_(a, r2, "PalID", pal)
            set_(a, r2, "WazaID", f"EPalWazaID::{move}")
            data.append(r2)


def verify(assets):
    a = assets[TABLES[0]]
    per_pal = {}
    for r in rows(a):
        per_pal.setdefault(str(get(r, "PalID")), set()).add(enum_short(get(r, "WazaID")))
    counts = {len(v) for v in per_pal.values()}
    if min(counts) < POOL_SIZE:
        return [f"certains pals ont moins de {POOL_SIZE} egg moves : min={min(counts)}"]
    return []
