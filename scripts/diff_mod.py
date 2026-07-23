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
    """Égalité tolérante, récursive : 'EPalFoo::Bar' ≡ 'Bar' (enums), et les
    structs/arrays UAssetAPI sont comparés par leur contenu sémantique."""
    if a == b:
        return True
    if isinstance(a, str) and isinstance(b, str):
        return a.split("::")[-1] == b.split("::")[-1]
    if isinstance(a, dict) and isinstance(b, dict):
        if a.get("Name") != b.get("Name"):
            return False
        return same(a.get("Value"), b.get("Value"))
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return False


def deep_changes(a, b, path=""):
    """Liste (chemin, avant, après) des feuilles qui diffèrent dans des
    structures UAssetAPI imbriquées (structs dans structs, arrays…)."""
    if same(a, b):
        return []
    if isinstance(a, dict) and isinstance(b, dict) and a.get("Name") == b.get("Name"):
        return deep_changes(a.get("Value"), b.get("Value"),
                            f"{path}.{a.get('Name')}" if path else str(a.get("Name")))
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            sub = f"{path}[{i}]"
            if isinstance(x, dict) and x.get("Name") not in (None, path.split(".")[-1]):
                sub = f"{path}.{x['Name']}" if path else str(x.get("Name"))
            out.extend(deep_changes(x, y, sub))
        return out
    return [(path or "?", a, b)]


def _compact(v):
    """Struct UAssetAPI → forme lisible {Name: Value} ; scalaires inchangés."""
    if isinstance(v, dict):
        if "Name" in v and "Value" in v:
            return {v["Name"]: _compact(v["Value"])}
        return {k: _compact(x) for k, x in v.items() if k in ("Name", "Value")} or v
    if isinstance(v, list):
        merged = {}
        plain = []
        for x in v:
            c = _compact(x)
            if isinstance(c, dict) and len(c) == 1:
                merged.update(c)
            else:
                plain.append(c)
        return merged if merged and not plain else plain or merged
    return v


def fmt(v, limit=60):
    v = _compact(v)
    s = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
    return s if len(s) <= limit else s[:limit] + "…"


NOISY = ("BodyInstance", "CollisionResponses", "RelativeScale", "CanCharacterStepUpOn")


def sort_leaves(leaves):
    """Gameplay d'abord, plomberie moteur (collisions…) ensuite."""
    return sorted(leaves, key=lambda t: any(n in t[0] for n in NOISY))


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
    leaves = []
    for f in mc:
        if not same(vc.get(f), mc.get(f)):
            leaves.extend(deep_changes(vc.get(f), mc.get(f), f))
    other = _diff_other_exports(vanilla, modded)
    if not leaves and not other:
        out.append("- CDO identique (changements dans le bytecode ou hors exports UObject)")
    leaves = sort_leaves(leaves)
    for path, a, b in leaves[:25]:
        out.append(f"  - `{path}` : {fmt(a, 90)} → {fmt(b, 90)}")
    if len(leaves) > 25:
        out.append(f"  - … +{len(leaves) - 25} autres feuilles modifiées")
    out.extend(other)


def _diff_other_exports(vanilla, modded, limit=10):
    """Exports non-CDO appariés par ObjectName (composants de BP, sous-objets)."""
    def emap(asset):
        return {str(e.get("ObjectName")): e for e in asset["Exports"]
                if not str(e.get("ObjectName", "")).startswith("Default__")
                and isinstance(e.get("Data"), list)}
    ve, me = emap(vanilla), emap(modded)
    per_export = []
    for name in me:
        if name not in ve:
            continue
        vp, mp = prop_map(ve[name]["Data"]), prop_map(me[name]["Data"])
        leaves = []
        for f in mp:
            if not same(vp.get(f), mp.get(f)):
                leaves.extend(deep_changes(vp.get(f), mp.get(f), f))
        if leaves:
            signal = sum(1 for p, _, _ in leaves if not any(n in p for n in NOISY))
            per_export.append((signal, name, sort_leaves(leaves)))
    out = []
    for signal, name, leaves in sorted(per_export, key=lambda t: -t[0]):
        for path, a, b in leaves[:limit]:
            out.append(f"  - `{name}.{path}` : {fmt(a, 90)} → {fmt(b, 90)}")
        if len(leaves) > limit:
            out.append(f"  - `{name}` : … +{len(leaves) - limit} feuilles (surtout plomberie collisions)")
    return out[:limit * 4]


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
