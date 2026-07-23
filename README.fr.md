*[English version](README.md)*

# palworld-mods

![CI](https://github.com/morgannito/palworld-mods/actions/workflows/ci.yml/badge.svg)
![GitHub release](https://img.shields.io/github/v/release/morgannito/palworld-mods)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Palworld 1.0](https://img.shields.io/badge/Palworld-v1.0.1.100619-blue)
![Server](https://img.shields.io/badge/server-Linux%20%7C%20no%20UE4SS-orange)

**38 mods server-side prêts à déposer** pour serveurs dédiés Palworld — des
patches datatable/Blueprint en `.pak` pur qui fonctionnent sur le **binaire
Linux natif** (là où les mods UE4SS ne tournent pas), plus le **pipeline
complet reproductible** pour bâtir les tiens.

## Installation

**→ [Tutoriel pas à pas](docs/INSTALL.fr.md)** (Linux, Docker, hébergeur
loué, Windows, solo — avec FAQ).

Version courte : télécharge les paks depuis les
[Releases](https://github.com/morgannito/palworld-mods/releases), dépose-les
dans `PalServer/Pal/Content/Paks/~mods/` (crée le dossier), restart. Rien à
installer côté joueurs — consoles crossplay incluses.

## Les mods

| Pak | Effet |
|---|---|
| `GTAPalpagos_P.pak` | Primes de crime ×20 — les PIDF très motivés |
| `JackpotChests_P.pak` | Chaque slot de coffre Grade2+ peut sortir une schematic légendaire (~2 %) |
| `ElementalDrops_P.pak` | Chaque pal droppe selon son élément (feu → organe igné, dragon → diamant…) |
| `GenerousAlphas_P.pak` | Boss alphas : schematic légendaire garantie + quantités doublées |
| `BoostedRelics_P.pak` | Reliques de l'Arbre-Monde ×4 (coffres et drops) |
| `CheapCrafting_P.pak` | Matériaux et travail ÷5 sur les 1414 recettes |
| `PalShopPimped_P.pak` | Les marchands de pals vendent aussi 8 légendaires (≤ lv50) |
| `LightningExpeditions_P.pak` | Expéditions ÷10 en durée (30 min → 3 min), récompenses ×5 |
| `RaidJackpot_P.pak` | Récompenses des raids de base ×10 |
| `MiracleFishing_P.pak` | Pêche : poissons Boss ×4, Nushi (légendaires) ×10 |
| `ExpressFriendship_P.pak` | Seuils d'amitié ÷5 (rangs négatifs aussi) |
| `MassiveOutbreaks_P.pak` | Hordes d'outbreak ×3 (cap 30), niveaux +3 — 9 biomes |
| `BetterBases_P.pak` | Ouvriers ×2/niveau (cap 50), 4 bases dès lv15, zéro maladie ni crise, cultures ÷5/×3, machines ×5, skill fruits rares ×2-3 |
| `CheapBuilding_P.pak` | Matériaux des 498 constructions ÷5, conso électrique ÷2, snap ×2.5 |
| `FastHaulers_P.pak` | TransportSpeed ×2 pour les 753 pals |
| `FastProgress_P.pak` | Recherches labo ÷5, chirurgie des passifs ÷5, points de tech ÷2 |
| `BiggerBases_P.pak` | Rayon de base 35 m → 70 m + spawns/raids repoussés + aspiration ×2 |
| `FeatherStacks_P.pak` | Poids des items ÷2, piles ×2 (équipements préservés) |
| `PurePassives_P.pak` | Les passifs perdent leurs malus (Musclehead sans le -50 % craft) |
| `CheapStatues_P.pak` | Statues de Pouvoir : moitié moins de reliques par rang |
| `ItemShopPimped_P.pak` | Boutiques : + sphères Tera, pierres IV, diamants, clés or (prix salés) |
| `DepressoWorld_P.pak` | La zone de départ ne spawn QUE des Depresso. 100 % meme |
| `CombatPlus_P.pak` | Cooldowns des 384 attaques -40 %, attaques faibles +30 % |
| `ArenaChampion_P.pak` | Récompenses de l'arène solo ×5 |
| `DungeonDeluxe_P.pak` | Coffres Grade_02 de fin de donjon ×4 |
| `CaptureScholar_P.pak` | Bonus d'XP de capture ×3 |
| `PondDeluxe_P.pak` | Mare à poissons : pals rares ×4 |
| `EarlyLearner_P.pak` | Attaques apprises au demi-niveau (5772 entrées ÷2) |
| `EpicBosses_P.pak` | Les 322 boss ont ×4 HP (raid bosses épargnés) |
| `LegendarySafari_P.pak` | Sky Island (lv 68-69) devient une réserve de légendaires sauvages |
| `OmniEggMoves_P.pak` | Le top-8 des attaques héritables transmissible par œuf à toutes les espèces |
| `PIDFElite_P.pak` | La police en mode SWAT : HP/attaque/défense ×3 |
| `DungeonRoulette_P.pak` | Les 160 boss de donjons rebrassés — n'importe quel boss n'importe où |
| `FrequentVisitors_P.pak` | Marchands ambulants dès le grade 1 (au lieu de 7), poids ×2 |
| `NightTerrors_P.pak` | La nuit, ~270 spawners s'éveillent avec des variantes _Dark +8 niveaux |
| `ArenaAllStars_P.pak` | Les 43 adversaires d'arène alignent des équipes légendaires/_Dark, talents max |
| `TowerTitans_P.pak` | Les 21 boss de tours doublent leurs HP : sièges marathon |
| `CheapSouls_P.pak` | Amélioration par âmes ÷2 sur les 20 rangs |

**Paks combinés** (bundles sans conflit, générés par `--combine`) :
`LootComplete_P.pak` (les 5 mods de loot), `WildSpawns_P.pak` (depresso +
safari + roulette + night-terrors), `PalStats_P.pak` (epic-bosses +
fast-haulers + tower-titans), `LootFiesta_P.pak` (legacy). Charger un combiné
**à la place de** ses composants.

## Pipeline (pour bâtir tes propres mods)

```
Pal-LinuxServer.pak ──repak──▶ gamedata/*.uasset ──uassetjson──▶ JSON
                                                        │ mods/<mod>/patch.py
dist/<Mod>_P.pak ◀──repak pack── staging/*.uasset ◀──uassetjson──┘
```

Prérequis, build, verify, workflow post-MAJ et déploiement : voir le
[README anglais](README.md#pipeline) (référence canonique) et les
[pièges documentés](README.md#hard-earned-gotchas). Analyses de mods tiers :
[docs/mod-analysis/](docs/mod-analysis/). Plan de test :
[docs/test-plan.md](docs/test-plan.md).

## Plus de docs

- **[Guide d'installation](docs/INSTALL.fr.md)** ([EN](docs/INSTALL.md)) — tous les setups, avec FAQ
- **[Plan de test](docs/test-plan.md)** — boot-test + checklist in-game
- **[Analyses de mods](docs/mod-analysis/)** — rétro-ingénierie des mods tiers populaires
- **[Changelog](CHANGELOG.md)** — le contenu de chaque release

## Licence & disclaimer

Scripts et patches : **MIT** (voir LICENSE). Les `.pak` de `dist/`
contiennent des datatables du jeu modifiées, distribuées gratuitement selon
l'usage établi de la communauté de modding Palworld (Nexus/CurseForge), sans
affiliation avec Pocketpair. Palworld © Pocketpair, Inc. Les assets bruts
(`gamedata/`) ne sont jamais commités. Cible : Palworld **v1.0.1.100619**.
