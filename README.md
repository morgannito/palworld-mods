*[Version française](README.fr.md)*

# palworld-mods

![GitHub release](https://img.shields.io/github/v/release/morgannito/palworld-mods)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Palworld 1.0](https://img.shields.io/badge/Palworld-v1.0.1.100619-blue)
![Server](https://img.shields.io/badge/server-Linux%20%7C%20no%20UE4SS-orange)

**30 drop-in server-side mods** for Palworld dedicated servers — pure `.pak`
datatable/Blueprint patches that work on the **native Linux binary** (the one
thing UE4SS mods can't do), plus the **full reproducible pipeline** to build
your own.

## Quick start

Grab the paks from [Releases](https://github.com/morgannito/palworld-mods/releases),
drop the ones you want into `PalServer/Pal/Content/Paks/~mods/` (create the
folder), restart the server. Nothing to install on clients — console crossplay
players included.

## The mods

| Pak | Effect |
|---|---|
| `GTAPalpagos_P.pak` | Crime bounties ×20 — the PIDF get very motivated |
| `JackpotChests_P.pak` | Every Grade2+ chest slot can roll a legendary schematic (~2 %) |
| `ElementalDrops_P.pak` | Every pal drops by element (fire → flame organ, dragon → diamond…) |
| `GenerousAlphas_P.pak` | Alpha bosses: guaranteed legendary schematic + doubled quantities |
| `BoostedRelics_P.pak` | World Tree relics ×4 (chests and pal drops) |
| `CheapCrafting_P.pak` | Materials and work ÷5 across all 1414 recipes |
| `PalShopPimped_P.pak` | Pal merchants also sell 8 legendaries (Jetragon, Frostallion…) up to lv50 |
| `LightningExpeditions_P.pak` | Expeditions ÷10 duration (30 min → 3 min), rewards ×5 |
| `RaidJackpot_P.pak` | Base raid rewards ×10 |
| `MiracleFishing_P.pak` | Fishing: Boss fish ×4, Nushi (legendary) ×10 |
| `ExpressFriendship_P.pak` | Friendship thresholds ÷5 (negative ranks too) |
| `MassiveOutbreaks_P.pak` | Outbreak hordes ×3 (cap 30), levels +3 — 9 biomes |
| `BetterBases_P.pak` | Workers ×2/level (cap 50), 4 guild bases by lv15, zero sickness or tantrums, crops ÷5/×3, machines ×5, rare skill fruits ×2-3 |
| `CheapBuilding_P.pak` | Materials of all 498 buildables ÷5, power draw ÷2, snap threshold ×2.5 (bye "not connected") |
| `FastHaulers_P.pak` | TransportSpeed ×2 for all 753 pals |
| `FastProgress_P.pak` | Lab research ÷5 (work + materials), passive surgery ÷5, tech points ÷2 |
| `BiggerBases_P.pak` | Base radius 35 m → 70 m (CDO patch of `BP_PalGameSetting`) + spawns/raids pushed outside the new radius + hauler pickup range ×2 |
| `FeatherStacks_P.pak` | All item weights ÷2, stacks ×2 (non-stackable gear preserved) |
| `PurePassives_P.pak` | Passives lose their downsides (Musclehead = +30 % attack without -50 % craft) |
| `CheapStatues_P.pak` | Statues of Power: half the relics per rank |
| `ItemShopPimped_P.pak` | Village shops: + Tera spheres, tier-IV upgrade stones, diamonds, gold keys (steep prices) |
| `DepressoWorld_P.pak` | The starting zone spawns ONLY Depresso. Zero utility, 100 % meme |
| `CombatPlus_P.pak` | All 384 attack cooldowns -40 %, weak attacks (<125) +30 % |
| `ArenaChampion_P.pak` | Solo arena rewards ×5 (first clear and reclears) |
| `DungeonDeluxe_P.pak` | Grade_02 end-of-dungeon chests ×4 in the lottery |
| `CaptureScholar_P.pak` | Capture bonus XP ×3 |
| `PondDeluxe_P.pak` | Fish pond: rare pals (dragons…) ×4 |
| `EarlyLearner_P.pak` | Pals learn their attacks at half the level (5772 entries ÷2) |
| `EpicBosses_P.pak` | All 322 bosses have ×4 HP — real 15-minute coop fights (raid bosses untouched) |
| `LegendarySafari_P.pak` | Sky Island (lv 68-69) becomes a wild legendary reserve (8-species pool) |

**Combined paks** (conflict-free bundles, built with `--combine`):
`LootComplete_P.pak` (all 5 loot mods), `WildSpawns_P.pak` (depresso-world +
legendary-safari), `PalStats_P.pak` (epic-bosses + fast-haulers),
`LootFiesta_P.pak` (legacy, 3 loot mods). Load a combined pak **instead of**
its components.

## Pipeline

```
Pal-LinuxServer.pak ──repak──▶ gamedata/*.uasset ──uassetjson──▶ JSON
                                                        │ mods/<mod>/patch.py
dist/<Mod>_P.pak ◀──repak pack── staging/*.uasset ◀──uassetjson──┘
```

### Prerequisites (once)

```sh
# .NET 10 user-space
curl -sL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 10.0 --install-dir ~/.dotnet
# repak
cargo install --git https://github.com/trumank/repak --rev v0.2.3 repak_cli
# UAssetAPI + the conversion tool
git clone --depth 1 https://github.com/atenfyr/UAssetAPI tools/UAssetAPI
(cd tools/UassetJson && PATH="$HOME/.dotnet:$PATH" dotnet build -c Release)
# game datatables (from your server's pak — never committed, Pocketpair copyright)
repak unpack --include "Pal/Content/Pal/DataTable/**" --include "Pal/Content/Pal/Blueprint/System/BP_PalGameSetting.*" --output gamedata Pal-LinuxServer.pak
```

`mappings/Mappings.usmap` (pinned commit
[PalworldModding/UsefulFiles@42cf396](https://github.com/PalworldModding/UsefulFiles/commit/42cf396e714c166f17950a9c964583e0cadf2a15),
published for 1.0) is required to decode the unversioned `.uasset` files.

### Build & verify

```sh
python3 scripts/build.py                 # all mods
python3 scripts/build.py gta-palpagos    # one mod
python3 scripts/build.py --conflicts     # table → mods map (deploy planning)
# merge into a single pak (REQUIRED when two mods patch the same table):
python3 scripts/build.py --combine LootFiesta jackpot-chests lightning-expeditions boosted-relics
# end-to-end check of every pak in dist/ (unpack, decode, diff vs vanilla, per-mod asserts):
python3 scripts/verify.py
# after a game update — re-extract, refresh usmap, rebuild, verify:
scripts/update.sh
# deploy a batch to the server (backup + safe restart + auto-rollback; requires DEPLOY=yes):
DEPLOY=yes scripts/deploy.sh dist/BetterBases_P.pak dist/BiggerBases_P.pak
```

Run `build.py --conflicts` for the live table → mods map. Current conflict
groups (one loaded pak per table — use the combined paks): the 5 loot mods
(`DT_ItemLotteryDataTable`, `DT_PalDropItem*`), epic-bosses + fast-haulers
(`DT_PalMonsterParameter*`), depresso-world + legendary-safari
(`DT_PalWildSpawner`).

### Deployment

One pak per table family. Copy to `PalServer/Pal/Content/Paks/~mods/`, chown
to the service user, clean restart. Server-side only.

## Hard-earned gotchas

- **FNames with numeric suffixes**: `Blueprint_SFBow_5` is FName
  (`Blueprint_SFBow`, 6) on the UE side — the NameMap only stores the base.
  `palmod.ensure_name()` applies the split rule (suffix `_N` without leading
  zero). `WorldTreeRelic_01` (leading zero) stays literal.
- **Every new string must enter the NameMap** of the JSON, otherwise
  `DummyFNameSerializationException` at write time.
- **`Rate2 = "+0"`** in drop tables: special value (slot tied to the previous
  roll), serialized as a string — don't cast to float, don't touch.
- **Byte-identical roundtrip validated** (sha256) before any patch: if
  UAssetAPI can't reproduce the original exactly, nothing else is reliable.
- **BP patches (bigger-bases)**: the Blueprint roundtrip is not byte-identical
  on the `.uasset` header (UAssetAPI re-normalizes NameMap + offsets,
  consistently) — the `.uexp` (data) stays identical; same mechanism as
  published UAssetGUI mods. Validate in-game after each game update.
- After a **game update**: re-extract `gamedata/`, refresh the `.usmap`,
  rebuild — a pak built on old tables overwrites the update's changes.

## License & disclaimer

Scripts and patches: **MIT** (see LICENSE). The `.pak` files in `dist/`
contain modified game datatables, distributed free of charge following
established Palworld modding community practice (Nexus/CurseForge), with no
affiliation with Pocketpair. Palworld © Pocketpair, Inc. Raw assets
(`gamedata/`) are never committed. Target: Palworld **v1.0.1.100619**.
