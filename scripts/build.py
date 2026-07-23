#!/usr/bin/env python3
"""Build des mods : gamedata (.uasset) -> JSON -> patch -> .uasset -> .pak

Usage : python3 scripts/build.py [mod ...]   (défaut : tous les mods/)
"""
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAMEDATA = REPO / "gamedata"
MAPPINGS = REPO / "mappings" / "Mappings.usmap"
UASSETJSON = REPO / "tools" / "UassetJson" / "bin" / "Release" / "net10.0" / "uassetjson"
REPAK = Path.home() / ".cargo" / "bin" / "repak"
BUILD = REPO / "build"
DIST = REPO / "dist"

ENV = {**os.environ, "DOTNET_ROOT": str(Path.home() / ".dotnet")}


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True, env=ENV, stdout=subprocess.DEVNULL)


def tojson(table, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    run(UASSETJSON, "tojson", GAMEDATA / f"{table}.uasset", out, MAPPINGS)


def fromjson(json_path, out_uasset):
    out_uasset.parent.mkdir(parents=True, exist_ok=True)
    run(UASSETJSON, "fromjson", json_path, out_uasset)


def load_mod(mod_dir):
    spec = importlib.util.spec_from_file_location(mod_dir.name, mod_dir / "patch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cached_json(table):
    """Cache read-only des tables sources en JSON."""
    cache = BUILD / "json-cache" / f"{table.replace('/', '_')}.json"
    if not cache.exists():
        tojson(table, cache)
    return cache


def build_mod(mod_dir):
    sys.path.insert(0, str(REPO / "scripts"))
    import palmod

    mod = load_mod(mod_dir)
    print(f"== {mod_dir.name} -> {mod.PAK_NAME}_P.pak")

    assets = {t: palmod.load(cached_json(t)) for t in mod.TABLES}
    extra = {t: palmod.load(cached_json(t)) for t in getattr(mod, "EXTRA", [])}
    mod.patch(assets, extra)

    staging = BUILD / "staging" / mod_dir.name
    if staging.exists():
        shutil.rmtree(staging)
    for table, asset in assets.items():
        patched_json = BUILD / "patched" / mod_dir.name / f"{Path(table).name}.json"
        patched_json.parent.mkdir(parents=True, exist_ok=True)
        palmod.save(asset, patched_json)
        fromjson(patched_json, staging / f"{table}.uasset")

    DIST.mkdir(exist_ok=True)
    pak = DIST / f"{mod.PAK_NAME}_P.pak"
    run(REPAK, "pack", "--version", "V11", staging, pak)
    subprocess.run([str(REPAK), "list", str(pak)], check=True, env=ENV)
    print(f"   OK {pak.relative_to(REPO)} ({pak.stat().st_size // 1024} Ko)")


def build_combined(pak_name, mod_dirs):
    """Fusionne plusieurs mods en un seul pak : patches appliqués séquentiellement
    sur les mêmes assets (résout les conflits « dernier pak chargé gagne »)."""
    sys.path.insert(0, str(REPO / "scripts"))
    import palmod

    mods = [load_mod(d) for d in mod_dirs]
    print(f"== combine {'+'.join(d.name for d in mod_dirs)} -> {pak_name}_P.pak")

    tables = sorted({t for m in mods for t in m.TABLES})
    extras = sorted({t for m in mods for t in getattr(m, "EXTRA", [])})
    assets = {t: palmod.load(cached_json(t)) for t in tables}
    extra = {t: palmod.load(cached_json(t)) for t in extras}
    for m in mods:
        m.patch({t: assets[t] for t in m.TABLES}, extra)

    staging = BUILD / "staging" / f"combined-{pak_name}"
    if staging.exists():
        shutil.rmtree(staging)
    for table, asset in assets.items():
        patched_json = BUILD / "patched" / f"combined-{pak_name}" / f"{Path(table).name}.json"
        patched_json.parent.mkdir(parents=True, exist_ok=True)
        palmod.save(asset, patched_json)
        fromjson(patched_json, staging / f"{table}.uasset")

    DIST.mkdir(exist_ok=True)
    pak = DIST / f"{pak_name}_P.pak"
    run(REPAK, "pack", "--version", "V11", staging, pak)
    print(f"   OK {pak.relative_to(REPO)} ({pak.stat().st_size // 1024} Ko)")


def main():
    args = sys.argv[1:]
    all_dirs = sorted(d for d in (REPO / "mods").iterdir() if (d / "patch.py").exists())

    if args and args[0] == "--combine":
        if len(args) < 3:
            sys.exit("usage: build.py --combine <NomPak> <mod> [mod ...]")
        chosen = [d for d in all_dirs if d.name in args[2:]]
        missing = set(args[2:]) - {d.name for d in chosen}
        if missing:
            sys.exit(f"mods inconnus : {', '.join(sorted(missing))}")
        build_combined(args[1], chosen)
        return

    mod_dirs = [d for d in all_dirs if d.name in args] if args else all_dirs
    if not mod_dirs:
        sys.exit("aucun mod à builder")
    for d in mod_dirs:
        build_mod(d)


if __name__ == "__main__":
    main()
