#!/usr/bin/env python3
"""Vérification end-to-end des paks de dist/ — les « tests » des mods.

Pour chaque pak :
1. dépaquetage repak
2. chaque table doit DIFFÉRER du vanilla (sha256 du .uexp vs gamedata/) —
   un patch sans effet est un échec
3. chaque .uasset doit se re-décoder proprement via uassetjson (mode complet)
4. si le patch.py du mod expose `verify(assets) -> list[str]`, ses assertions
   tournent sur les tables décodées du pak

Usage : python3 scripts/verify.py [--fast] [pak ...]
        --fast : saute le décodage (sha-diff + hooks uniquement)
Sortie : rapport par pak, exit 1 au moindre échec.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAMEDATA = REPO / "gamedata"
MAPPINGS = REPO / "mappings" / "Mappings.usmap"
UASSETJSON = REPO / "tools" / "UassetJson" / "bin" / "Release" / "net10.0" / "uassetjson"
REPAK = Path.home() / ".cargo" / "bin" / "repak"
DIST = REPO / "dist"
ENV = {**os.environ, "DOTNET_ROOT": str(Path.home() / ".dotnet")}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_mods_by_pakname():
    sys.path.insert(0, str(REPO / "scripts"))
    mods = {}
    for d in sorted((REPO / "mods").iterdir()):
        if not (d / "patch.py").exists():
            continue
        spec = importlib.util.spec_from_file_location(d.name, d / "patch.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mods[mod.PAK_NAME] = mod
    return mods


def decode(uasset, out):
    r = subprocess.run(
        [str(UASSETJSON), "tojson", str(uasset), str(out), str(MAPPINGS)],
        env=ENV, capture_output=True,
    )
    return r.returncode == 0


def verify_pak(pak, mods, fast):
    failures = []
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s) / "unpacked"
        r = subprocess.run([str(REPAK), "unpack", "--output", str(tmp), str(pak)],
                           env=ENV, capture_output=True)
        if r.returncode != 0:
            return [f"dépaquetage impossible : {r.stderr.decode()[:120]}"]

        decoded = {}
        for ua in sorted(tmp.rglob("*.uasset")):
            rel = ua.relative_to(tmp)
            table = str(rel.with_suffix(""))

            uexp, vanilla_uexp = ua.with_suffix(".uexp"), GAMEDATA / rel.with_suffix(".uexp")
            if uexp.exists() and vanilla_uexp.exists() and sha(uexp) == sha(vanilla_uexp):
                failures.append(f"{rel.name} : identique au vanilla (patch sans effet ?)")

            if not fast:
                out = Path(tmp_s) / (table.replace("/", "_") + ".json")
                if decode(ua, out):
                    decoded[table] = out
                else:
                    failures.append(f"{rel.name} : re-décodage impossible (asset corrompu ?)")

        mod = mods.get(pak.stem.removesuffix("_P"))
        if mod is None:
            failures.append("info: pak combiné ou orphelin — checks génériques uniquement")
        elif hasattr(mod, "verify"):
            missing = [t for t in mod.TABLES if t not in decoded]
            if fast:
                for t in mod.TABLES:
                    out = Path(tmp_s) / (t.replace("/", "_") + ".json")
                    if decode(tmp / f"{t}.uasset", out):
                        decoded[t] = out
                missing = [t for t in mod.TABLES if t not in decoded]
            if missing:
                failures.append(f"verify() non exécuté, tables manquantes : {missing}")
            else:
                assets = {t: json.load(open(decoded[t])) for t in mod.TABLES}
                failures.extend(mod.verify(assets))
    return failures


def main():
    args = [a for a in sys.argv[1:]]
    fast = "--fast" in args
    wanted = [a for a in args if a != "--fast"]

    mods = load_mods_by_pakname()
    paks = sorted(DIST.glob("*.pak"))
    if wanted:
        paks = [p for p in paks if p.stem in wanted or p.name in wanted]
    if not paks:
        sys.exit("aucun pak dans dist/")

    total_fail = 0
    for pak in paks:
        failures = verify_pak(pak, mods, fast)
        real = [f for f in failures if not f.startswith("info:")]
        status = "OK " if not real else "FAIL"
        print(f"[{status}] {pak.name}")
        for f in failures:
            print(f"       - {f}")
        total_fail += len(real)

    print(f"\n{len(paks)} paks vérifiés, {total_fail} échec(s)")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
