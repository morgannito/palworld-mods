# Changelog

All releases target Palworld **v1.0.1.100619**. Full paks attached to each
[GitHub release](https://github.com/morgannito/palworld-mods/releases).

## v1.6 — 2026-07-23

- **TowerTitans**: the 21 tower bosses double their HP (vanilla rates vary
  12×-405× and are respected). **CheapSouls**: pal enhancement soul costs ÷2.
- `PalStats_P` combined pak now bundles epic-bosses + fast-haulers +
  tower-titans.
- The `verify.py` harness caught a wrong test assumption live (tower boss
  rates are not uniform) — working as intended.

## v1.5 — 2026-07-23

- **NightTerrors**: at night ~270 extra spawners wake up with _Dark variants,
  +8 levels (uses the vanilla `OnlyTime::Night` mechanic). **ArenaAllStars**:
  the 43 arena opponents field remixed legendary/_Dark teams, maxed talents.
- `WildSpawns_P` now bundles 4 spawn mods.
- Explored and ruled out: wild-egg lottery (no datatable — hatch logic lives
  in Blueprint code), weather-gated spawns (`OnlyWeather` unused by vanilla),
  curveball physics (client-side).

## v1.4 — 2026-07-23

- **OmniEggMoves**: top-8 inheritable attacks breedable onto every species
  (pool computed dynamically from game tables). **PIDFElite**: police ×3.
  **DungeonRoulette**: 160 dungeon bosses reshuffled. **FrequentVisitors**:
  wandering merchants from grade 1.

## v1.3 — 2026-07-23

- **EarlyLearner** (attack learn levels ÷2), **EpicBosses** (322 bosses ×4 HP,
  raid bosses spared), **LegendarySafari** (Sky Island = wild legendary
  reserve).
- Official combined paks: `LootComplete`, `WildSpawns`, `PalStats`.
- Ops tooling: `scripts/update.sh` (post-game-update workflow) and
  `scripts/deploy.sh` (backup + safe restart + auto-rollback, gated behind
  `DEPLOY=yes`).
- `diff_mod.py` v2: recursive nested-struct diffs.
- Boot-test on a native Linux x86 server (Docker): 24 paks mounted, 59 FPS,
  zero crashes (`docs/test-plan.md`).

## v1.2 — 2026-07-23

- **CombatPlus** (cooldowns -40 %, weak attacks +30 %), **ArenaChampion**
  (rewards ×5), **DungeonDeluxe** (Grade_02 chests ×4), **CaptureScholar**
  (capture XP ×3), **PondDeluxe** (rare pond pals ×4).

## v1.1 — 2026-07-23

- **FeatherStacks** (weights ÷2, stacks ×2), **PurePassives** (no downsides),
  **CheapStatues** (relic costs ÷2), **ItemShopPimped** (premium shop stock),
  **DepressoWorld** (meme), **BiggerBases** (base radius 70 m — first
  Blueprint CDO patch), **FastProgress** (lab/surgery/tech costs down).

## v1.0 — 2026-07-23

- Initial release: 17 datatable mods (loot, bases, crafting, breeding-adjacent
  QoL, crime, expeditions, raids, fishing, friendship, outbreaks…) + the full
  pipeline (`uassetjson` C# tool on UAssetAPI, `palmod.py` helpers,
  `build.py` with `--combine` and `--conflicts`, byte-identical roundtrip
  validation, pinned 1.0 `.usmap`).
