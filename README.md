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
repak unpack --include "Pal/Content/Pal/DataTable/**" --output gamedata Pal-LinuxServer.pak
```

Le fichier `mappings/Mappings.usmap` (commit épinglé
[PalworldModding/UsefulFiles@42cf396](https://github.com/PalworldModding/UsefulFiles/commit/42cf396e714c166f17950a9c964583e0cadf2a15),
publié pour la 1.0) est indispensable au décodage des `.uasset` unversioned.

### Build

```sh
python3 scripts/build.py                # tous les mods
python3 scripts/build.py gta-palpagos   # un seul
```

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
- Après une **MAJ du jeu** : re-extraire `gamedata/`, mettre à jour le `.usmap`,
  rebuilder — un pak bâti sur d'anciennes tables écrase les nouveautés de la MAJ.

## Licence

Scripts et patches : MIT. Les assets du jeu (gamedata/, dist/) appartiennent à
Pocketpair et ne sont pas distribués dans ce repo.
