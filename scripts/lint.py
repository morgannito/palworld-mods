#!/usr/bin/env python3
"""Lint des mods — tourne en CI (sans gamedata) et en local.

Vérifie pour chaque mods/*/patch.py : syntaxe, import, contrat (PAK_NAME,
TABLES, patch()), unicité des PAK_NAME, docstring, et que chaque mod est
documenté dans les deux README.
"""
import ast
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

errors = []
warnings = []
pak_names = {}

mod_dirs = sorted(d for d in (REPO / "mods").iterdir() if (d / "patch.py").exists())
if not mod_dirs:
    sys.exit("aucun mod trouvé")

for d in mod_dirs:
    src = (d / "patch.py").read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        errors.append(f"{d.name}: erreur de syntaxe — {e}")
        continue

    if not ast.get_docstring(tree):
        warnings.append(f"{d.name}: pas de docstring")

    spec = importlib.util.spec_from_file_location(d.name, d / "patch.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        errors.append(f"{d.name}: import impossible — {type(e).__name__}: {e}")
        continue

    name = getattr(mod, "PAK_NAME", None)
    if not name or not isinstance(name, str):
        errors.append(f"{d.name}: PAK_NAME manquant ou invalide")
        continue
    if name in pak_names:
        errors.append(f"{d.name}: PAK_NAME '{name}' déjà utilisé par {pak_names[name]}")
    pak_names[name] = d.name

    tables = getattr(mod, "TABLES", None)
    if not tables or not all(isinstance(t, str) and t.startswith("Pal/") for t in tables):
        errors.append(f"{d.name}: TABLES manquant ou chemins invalides")
    if not callable(getattr(mod, "patch", None)):
        errors.append(f"{d.name}: patch() manquant")
    v = getattr(mod, "verify", None)
    if v is not None and not callable(v):
        errors.append(f"{d.name}: verify présent mais non callable")

readmes = {p: (REPO / p).read_text(encoding="utf-8") for p in ("README.md", "README.fr.md")}
for name, mod_dir in sorted(pak_names.items()):
    for rp, content in readmes.items():
        if f"{name}_P.pak" not in content:
            errors.append(f"{mod_dir}: `{name}_P.pak` absent de {rp}")

shared = {}
for d in mod_dirs:
    spec = importlib.util.spec_from_file_location(f"c_{d.name}", d / "patch.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        continue
    for t in getattr(mod, "TABLES", []):
        shared.setdefault(t, []).append(d.name)
conflict_count = sum(1 for m in shared.values() if len(m) > 1)

print(f"{len(mod_dirs)} mods, {len(pak_names)} PAK_NAME uniques, "
      f"{conflict_count} tables partagées (voir --conflicts)")
for w in warnings:
    print(f"  warn: {w}")
for e in errors:
    print(f"  ERREUR: {e}")
sys.exit(1 if errors else 0)
