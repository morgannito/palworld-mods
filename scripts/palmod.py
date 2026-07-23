"""Helpers d'édition des DataTables Palworld (JSON UAssetAPI)."""
import copy
import json
import re


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(asset, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asset, f, indent=2, ensure_ascii=False)


def rows(asset):
    return asset["Exports"][0]["Table"]["Data"]


def prop(row, name):
    for p in row["Value"]:
        if p["Name"] == name:
            return p
    raise KeyError(f"prop {name} absente de la row {row['Name']}")


def get(row, name):
    return prop(row, name).get("Value")


def set_(asset, row, name, value):
    p = prop(row, name)
    p["Value"] = value
    if isinstance(value, str):
        ensure_name(asset, value)


def _fname_key(name):
    """Convention UE : 'Blueprint_SFBow_5' = FName('Blueprint_SFBow', 6).

    Le suffixe _N (N numérique sans zéro de tête) est un numéro d'instance :
    seule la base est stockée dans la NameMap. 'WorldTreeRelic_01' (zéro de
    tête) reste un nom littéral entier.
    """
    m = re.match(r"^(.*)_(0|[1-9][0-9]*)$", name)
    return m.group(1) if m else name


def ensure_name(asset, name):
    """Les FName doivent exister dans la NameMap de l'asset."""
    nm = asset.get("NameMap")
    if nm is None:
        return
    key = _fname_key(name)
    if key not in nm and name not in nm:
        nm.append(key)


def clone_row(asset, row, new_name):
    r2 = copy.deepcopy(row)
    r2["Name"] = new_name
    ensure_name(asset, new_name)
    return r2


def enum_short(value):
    """'EPalElementType::Fire' -> 'Fire'"""
    return str(value).split("::")[-1]


def bp_defaults(asset):
    """Data du Class Default Object d'un Blueprint (export Default__*)."""
    for e in asset["Exports"]:
        if str(e.get("ObjectName", "")).startswith("Default__"):
            return e["Data"]
    raise KeyError("aucun export Default__ (CDO) dans cet asset")


def bp_prop(asset, name):
    for p in bp_defaults(asset):
        if p["Name"] == name:
            return p
    raise KeyError(f"prop {name} absente du CDO")
