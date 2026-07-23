"""Arena All-Stars — les 43 adversaires de l'arène solo alignent des équipes
remixées de légendaires et de variantes _Dark (choix déterministe), avec
talents maximisés. Chaque montée de rang devient un vrai combat d'exhibition.

Niveaux vanilla conservés : plus dur, pas injuste.
"""
import hashlib

from palmod import ensure_name, get, prop, rows, set_

PAK_NAME = "ArenaAllStars"
TABLES = ["Pal/Content/Pal/DataTable/Arena/DT_ArenaSoloNPCTable"]
EXTRA = ["Pal/Content/Pal/DataTable/Character/DT_PalMonsterParameter"]


def _pool(params):
    legendaries = [
        "JetDragon", "IceHorse", "BlackCentaur", "SaintCentaur",
        "NightLady", "MoonQueen", "Horus", "GoldenHorse",
    ]
    darks = sorted(
        r["Name"] for r in rows(params)
        if r["Name"].endswith("_Dark")
        and not r["Name"].startswith(("BOSS_", "RAID_", "SUMMON_", "PREDATOR_"))
    )
    return legendaries + darks


def _pick(pool, key):
    h = int(hashlib.sha1(key.encode()).hexdigest(), 16)
    return pool[h % len(pool)]


def patch(assets, extra):
    a = assets[TABLES[0]]
    pool = _pool(extra[EXTRA[0]])
    for r in rows(a):
        set_(a, r, "TalentLevel", 100)
        for i, otomo in enumerate(prop(r, "OtomoList")["Value"]):
            for p in otomo["Value"]:
                if p["Name"] == "PalId":
                    pal = _pick(pool, f"{r['Name']}/{i}")
                    p["Value"][0]["Value"] = pal
                    ensure_name(a, pal)


def verify(assets):
    a = assets[TABLES[0]]
    fails = []
    pals = set()
    for r in rows(a):
        if int(get(r, "TalentLevel")) != 100:
            fails.append(f"{r['Name']} TalentLevel != 100")
            break
        for otomo in prop(r, "OtomoList")["Value"]:
            for p in otomo["Value"]:
                if p["Name"] == "PalId":
                    pals.add(p["Value"][0]["Value"])
    if len(pals) < 10:
        fails.append(f"diversité des équipes trop faible : {len(pals)}")
    return fails
