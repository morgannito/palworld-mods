# palworld-mods

Mods datatable server-side pour Palworld 1.0 (serveur dédié Linux, paks purs `~mods`,
zéro UE4SS). Pipeline reproductible : extraction → JSON → patch Python → repack.

## Les mods

| Pak | Effet |
|---|---|
| `GTAPalpagos_P.pak` | Primes de crime ×20 — chaque délit rend les PIDF très motivés |
| `JackpotChests_P.pak` | Tous les coffres Grade2+ peuvent sortir une schematic légendaire (~2 %/slot) |
| `ElementalDrops_P.pak` | Chaque pal droppe selon son élément (feu → organe igné, dragon → diamant, terre → rubis…) |
| `GenerousAlphas_P.pak` | Boss alphas : schematic légendaire garantie + quantités doublées |
| `BoostedRelics_P.pak` | Reliques de l'Arbre-Monde ×4 (coffres et drops de pals) |
| `CheapCrafting_P.pak` | Matériaux et temps de craft ÷5 sur les 1414 recettes |
| `PalShopPimped_P.pak` | Les marchands de pals vendent aussi 8 légendaires (Jetragon, Frostallion…) niveau ≤50 |
| `LightningExpeditions_P.pak` | Expéditions ÷10 en durée (30 min → 3 min), récompenses ×5 |
| `RaidJackpot_P.pak` | Récompenses des raids de base ×10 |
| `MiracleFishing_P.pak` | Pêche : poissons Boss ×4, Nushi (légendaires) ×10 |
| `ExpressFriendship_P.pak` | Seuils d'amitié ÷5 (rangs négatifs aussi : pardon plus rapide) |
| `MassiveOutbreaks_P.pak` | Hordes d'outbreak ×3 (cap 30), niveaux +3 — 9 biomes |
| `BetterBases_P.pak` | Bases : ouvriers ×2/niveau (cap 50), 4 bases dès lv15, zéro maladie ni pétage de plombs, cultures ÷5/×3, machines ×5, skill fruits rares ×2-3 |
| `CheapBuilding_P.pak` | Matériaux des 498 constructions ÷5, conso électrique ÷2, snap de connexion ×2.5 (adieu « not connected ») |
| `FastHaulers_P.pak` | TransportSpeed ×2 pour les 753 pals — le portage à la base cesse d'être un supplice |
| `FastProgress_P.pak` | Recherches labo ÷5 (travail + matériaux), chirurgie des passifs ÷5, points de technologie ÷2 |
| `BiggerBases_P.pak` | Rayon de base 35 m → 70 m (patch CDO `BP_PalGameSetting`) + spawns/raids repoussés hors du rayon + aspiration transporteurs ×2 |
| `FeatherStacks_P.pak` | Poids de tous les items ÷2, piles ×2 (équipements non empilables préservés) |
| `PurePassives_P.pak` | Les passifs perdent leurs malus (Musclehead = +30 % attaque sans le -50 % craft) |
| `CheapStatues_P.pak` | Statues de Pouvoir : moitié moins de reliques par rang |
| `ItemShopPimped_P.pak` | Boutiques des villages : + sphères Tera, pierres IV, diamants, clés or (prix salés) |
| `DepressoWorld_P.pak` | La zone de départ ne spawn QUE des Depresso. Zéro utilité, 100 % meme |
| `CombatPlus_P.pak` | Cooldowns des 384 attaques -40 %, attaques faibles (<125) +30 % |
| `ArenaChampion_P.pak` | Récompenses de l'arène solo ×5 (first clear et reclears) |
| `DungeonDeluxe_P.pak` | Coffres Grade_02 de fin de donjon ×4 dans la loterie |
| `CaptureScholar_P.pak` | Bonus d'XP de capture ×3 |
| `PondDeluxe_P.pak` | Mare à poissons : pals rares (dragons…) ×4 |

Chaque mod patche une ou plusieurs DataTables :

- Crime : `DT_WorldSecurity_CrimeMasterDataTable` (champ `BaseReward`)
- Loterie coffres : `DT_ItemLotteryDataTable` (8777 rows, slots pondérés par zone/grade)
- Drops pals : `DT_PalDropItem` + `DT_PalDropItem_Common` (10 slots item/rate/min/max par pal)
- Recettes : `DT_ItemRecipeDataTable` + `_Common`
- Mapping pal→élément (lecture seule) : `DT_PalMonsterParameter`

## Pipeline

```
Pal-LinuxServer.pak ──repak──▶ gamedata/*.uasset ──uassetjson──▶ JSON
                                                        │ mods/<mod>/patch.py
dist/<Mod>_P.pak ◀──repak pack── staging/*.uasset ◀──uassetjson──┘
```

### Prérequis (une fois)

```sh
# .NET 10 user-space
curl -sL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 10.0 --install-dir ~/.dotnet
# repak
cargo install --git https://github.com/trumank/repak --rev v0.2.3 repak_cli
# UAssetAPI + outil de conversion
git clone --depth 1 https://github.com/atenfyr/UAssetAPI tools/UAssetAPI
(cd tools/UassetJson && PATH="$HOME/.dotnet:$PATH" dotnet build -c Release)
# datatables du jeu (depuis le pak du serveur, non commitées — copyright Pocketpair)
repak unpack --include "Pal/Content/Pal/DataTable/**" --include "Pal/Content/Pal/Blueprint/System/BP_PalGameSetting.*" --output gamedata Pal-LinuxServer.pak
```

Le fichier `mappings/Mappings.usmap` (commit épinglé
[PalworldModding/UsefulFiles@42cf396](https://github.com/PalworldModding/UsefulFiles/commit/42cf396e714c166f17950a9c964583e0cadf2a15),
publié pour la 1.0) est indispensable au décodage des `.uasset` unversioned.

### Build

```sh
python3 scripts/build.py                # tous les mods
python3 scripts/build.py gta-palpagos   # un seul
# fusion en un seul pak (OBLIGATOIRE si deux mods patchent la même table) :
python3 scripts/build.py --combine LootFiesta jackpot-chests lightning-expeditions boosted-relics
```

Tables partagées à surveiller : `DT_ItemLotteryDataTable` (jackpot-chests,
lightning-expeditions, boosted-relics) et `DT_PalDropItem*` (elemental-drops,
generous-alphas, boosted-relics) — un seul pak chargé par table, sinon le
dernier écrase les autres.

Sortie dans `dist/` (gitignoré : les paks contiennent des assets dérivés du jeu).

### Déploiement (manuel, jamais automatique)

Un seul pak par famille de tables (deux paks patchant la même table = le dernier
chargé gagne). Copier dans `PalServer/Pal/Content/Paks/~mods/`, owner du service,
puis restart propre. Server-side only : rien à installer côté clients.

## Pièges appris (le savoir durement acquis)

- **FName à suffixe numérique** : `Blueprint_SFBow_5` = FName(`Blueprint_SFBow`, 6)
  côté UE — la NameMap ne stocke que la base. `palmod.ensure_name()` applique la
  règle de split (suffixe `_N` sans zéro de tête). `WorldTreeRelic_01` (zéro de
  tête) reste littéral.
- **Toute string nouvelle doit entrer dans la NameMap** du JSON, sinon
  `DummyFNameSerializationException` au write.
- **`Rate2 = "+0"`** dans les drops : valeur spéciale (slot lié au tirage
  précédent), sérialisée en string — ne pas convertir en float, ne pas toucher.
- **Roundtrip validé byte-identique** (sha256) avant tout patch : si UAssetAPI ne
  reproduit pas l'original à l'identique, rien d'autre n'est fiable.
- **BP patch (bigger-bases)** : le roundtrip d'un Blueprint n'est pas byte-identique
  côté header `.uasset` (UAssetAPI re-normalise NameMap + offsets, de façon
  cohérente) — le `.uexp` (données) reste identique ; c'est la même mécanique que
  les mods UAssetGUI publiés. Valider en jeu après chaque MAJ.
- Après une **MAJ du jeu** : re-extraire `gamedata/`, mettre à jour le `.usmap`,
  rebuilder — un pak bâti sur d'anciennes tables écrase les nouveautés de la MAJ.

## Licence & disclaimer

Scripts et patches : **MIT**. Les `.pak` de `dist/` contiennent des datatables
du jeu modifiées — ils sont distribués selon l'usage établi de la communauté
de modding Palworld (Nexus/CurseForge), gratuitement et sans affiliation avec
Pocketpair. Palworld © Pocketpair, Inc. Les assets bruts (`gamedata/`) ne sont
jamais commités. Cible : Palworld **v1.0.1.100619** — rebuilder après toute MAJ.
