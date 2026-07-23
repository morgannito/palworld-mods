# Mod analysis — what popular mods actually change

Reverse-engineered reports produced by [`scripts/diff_mod.py`](../../scripts/diff_mod.py):
each third-party pak is unpacked and diffed against vanilla game tables, field
by field. Analysis only — **no third-party files are redistributed here**. All
credit goes to the original authors; links below.

| Report | Mod (author) | Key findings |
|---|---|---|
| [EasyPalExpedition](EasyPalExpedition.md) | [Easy PalExpeditions](https://www.curseforge.com/palworld/patch-pak-mods/easy-palexpeditions) | Expeditions 1800→**60 s**, required strength →1000 (÷25-200), and **removes ChallengeConditions** (no boss kill needed to unlock) — more aggressive than documented |
| [WoodBreedFarm](WoodBreedFarm.md) | [Wood Breed Farm](https://www.curseforge.com/palworld/patch-pak-mods/wood-breed-farm-egg) (MoxxyHaven) | CDO unchanged — the ingredient/timer edits live in nested `BreedFarmParameter` structs (current differ limit) |
| [LessRestrictive](LessRestrictive.md) | [Less Restrictive Building](https://www.curseforge.com/palworld/patch-pak-mods/less-restrictive-building-pak) | Patches **dozens of BuildObject BPs** one by one: `bSpawnableIfOverlapped=True`, `DefaultMobility=Movable` — a per-object collision approach, complementary to our global snap-threshold method |
| [BetterNightLight](BetterNightLight.md) | [Better Night Light](https://www.curseforge.com/palworld/patch-pak-mods/better-night-light) | Replaces two PostProcess assets under `Content/Others/nakano_test/` (a Pocketpair dev's test folder that shipped in the game!) — visual, no datatable |

## Method

```sh
python3 scripts/diff_mod.py path/to/mod.zip --out docs/mod-analysis/Name.md
```

If a report says "vanilla absent from gamedata/", extract the listed asset from
your server pak first (command included in the report).

Known limits: nested struct diffs inside Blueprint CDOs are not expanded
(reported as "CDO identical"), and non-UObject assets (PostProcess curves,
textures) are listed but not diffed.
