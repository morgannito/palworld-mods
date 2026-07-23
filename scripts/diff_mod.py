#!/usr/bin/env python3
"""diff_mod — rétro-ingénierie d'un pak tiers : qu'est-ce qu'il change, exactement ?

Compare chaque asset du pak aux tables vanilla de gamedata/ et sort un rapport
markdown : rows ajoutées/supprimées/modifiées (DataTables), propriétés du CDO
modifiées (Blueprints), assets non comparables (vanilla absent ou binaire).

Usage : python3 scripts/diff_mod.py <mod.pak|mod.zip> [--out rapport.md]
"""
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAMEDATA = REPO / "gamedata"
MAPPINGS = REPO / "mappings" / "Mappings.usmap"
UASSETJSON = REPO / "tools" / "UassetJson" / "bin" / "Release" / "net10.0" / "uassetjson"
REPAK = Path.home() / ".cargo" / "bin" / "repak"
ENV = {**os.environ, "DOTNET_ROOT": str(Path.home() / ".dotnet")}


def decode(uasset, out):
    r = subprocess.run([str(UASSETJSON), "tojson", str(uasset), str(out), str(MAPPINGS)],
                       env=ENV, capture_output=True)
    return r.returncode == 0


def prop_map(row_value):
    return {p["Name"]: p.get("Value") for p in row_value}


def same(a, b):
    """Égalité tolérante : 'EPalFoo::Bar' et 'Bar' sont le même enum sérialisé
    différemment selon la version d'UAssetAPI qui a produit l'asset."""
    if a == b:
        return True
    if isinstance(a, str) and isinstance(b, str):
        return a.split("::")[-1] == b.split("::")[-1]
    return False


def fmt(v, limit=60):
    s = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
    return s if len(s) <= limit else s[:limit] + "…"


def diff_datatable(vanilla, modded, out):
    v_rows = {r["Name"]: r for r in vanilla["Exports"][0]["Table"]["Data"]}
    m_rows = {r["Name"]: r for r in modded["Exports"][0]["Table"]["Data"]}

    added = [n for n in m_rows if n not in v_rows]
    removed = [n for n in v_rows if n not in m_rows]
    changed = []
    for name in m_rows:
        if name not in v_rows:
            continue
        vp, mp = prop_map(v_rows[name]["Value"]), prop_map(m_rows[name]["Value"])
        fields = [(f, vp.get(f), mp.get(f)) for f in mp if not same(vp.get(f), mp.get(f))]
        if fields:
            changed.append((name, fields))

    out.append(f"- rows : {len(v_rows)} vanilla → {len(m_rows)} moddées "
               f"(+{len(added)} / -{len(removed)} / ~{len(changed)} modifiées)")
    for n in added[:10]:
        out.append(f"  - **ajoutée** `{n}` : {fmt(prop_map(m_rows[n]['Value']), 150)}")
    if len(added) > 10:
        out.append(f"  - … et {len(added) - 10} autres rows ajoutées")
    for n in removed[:10]:
        out.append(f"  - **supprimée** `{n}`")
    for name, fields in changed[:15]:
        det = ", ".join(f"{f}: {fmt(a)} → {fmt(b)}" for f, a, b in fields[:6])
        more = f" (+{len(fields) - 6} champs)" if len(fields) > 6 else ""
        out.append(f"  - `{name}` : {det}{more}")
    if len(changed) > 15:
        seen = {}
        for _, fields in changed:
            for f, _, _ in fields:
                seen[f] = seen.get(f, 0) + 1
        summary = ", ".join(f"{f} (×{c})" for f, c in sorted(seen.items(), key=lambda x: -x[1])[:8])
        out.append(f"  - … {len(changed) - 15} autres rows ; champs touchés : {summary}")


def diff_blueprint(vanilla, modded, out):
    def cdo(asset):
        for e in asset["Exports"]:
            if str(e.get("ObjectName", "")).startswith("Default__"):
                return prop_map(e.get("Data", []))
        return None

    vc, mc = cdo(vanilla), cdo(modded)
    if vc is None or mc is None:
        out.append("- pas de CDO comparable (asset non-datatable, non-BP ou structure inattendue)")
        return
    fields = [(f, vc.get(f), mc.get(f)) for f in mc if not same(vc.get(f), mc.get(f))]
    if not fields:
        out.append("- CDO identique (les changements sont ailleurs : bytecode, structs profonds…)")
    for f, a, b in fields[:20]:
        out.append(f"  - `{f}` : {fmt(a, 100)} → {fmt(b, 100)}")


def analyze(pak_path, report):
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        if pak_path.suffix == ".zip":
            with zipfile.ZipFile(pak_path) as z:
                z.extractall(tmp / "zip")
            paks = list((tmp / "zip").rglob("*.pak"))
            if not paks:
                report.append("aucun .pak dans le zip")
                return
            pak_path = paks[0]

        unpacked = tmp / "unpacked"
        subprocess.run([str(REPAK), "unpack", "--output", str(unpacked), str(pak_path)],
                       env=ENV, capture_output=True, check=True)

        info = subprocess.run([str(REPAK), "info", str(pak_path)], env=ENV,
                              capture_output=True, text=True).stdout
        mount = next((l.split(": ", 1)[1] for l in info.splitlines() if l.startswith("mount point")), "?")
        report.append(f"mount point `{mount.strip()}`\n")

        for ua in sorted(unpacked.rglob("*.uasset")):
            rel = ua.relative_to(unpacked)
            report.append(f"### `{rel}`")
            vanilla_ua = GAMEDATA / rel
            if not vanilla_ua.exists():
                report.append(f"- vanilla absent de gamedata/ — extraire avec :\n"
                              f"  `repak unpack --include \"{rel.with_suffix('')}.*\" --output gamedata Pal-LinuxServer.pak`")
                report.append("")
                continue
            vj, mj = tmp / "v.json", tmp / "m.json"
            if not (decode(vanilla_ua, vj) and decode(ua, mj)):
                report.append("- décodage impossible (usmap d'une autre version du jeu ?)")
                report.append("")
                continue
            vanilla, modded = json.load(open(vj)), json.load(open(mj))
            is_dt = any("DataTableExport" in e["$type"] for e in vanilla["Exports"])
            (diff_datatable if is_dt else diff_blueprint)(vanilla, modded, report)
            report.append("")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    out_path = None
    if "--out" in sys.argv:
        out_path = Path(sys.argv[sys.argv.index("--out") + 1])

    report = [f"# Analyse : {src.name}\n"]
    analyze(src, report)
    text = "\n".join(report)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"rapport → {out_path}")
    else:
        print(text)


if __name__ == "__main__":
    main()
