# Plan de test in-game

Deux niveaux : **boot-test** (le serveur charge les paks sans crash — automatisable),
puis **gameplay** (les effets sont visibles en jeu — manuel, ~20 min).

## Lot de déploiement (24 paks, zéro conflit)

Tous les mods **sauf** les 9 composants couverts par les combinés :
`LootComplete_P` remplace jackpot-chests + lightning-expeditions +
boosted-relics + elemental-drops + generous-alphas ; `WildSpawns_P` remplace
depresso-world + legendary-safari ; `PalStats_P` remplace epic-bosses +
fast-haulers. `LootFiesta_P` (legacy) exclu.

## Boot-test (serveur dédié Linux, Docker)

```sh
docker run -d --name palworld-boottest --platform linux/amd64 \
  -v "$PWD/testserver:/palworld" \
  -e PORT=8211 -e COMMUNITY=false -e REST_API_ENABLED=true -e REST_API_PORT=8212 \
  thijsvanloef/palworld-server-docker:latest
# poser les paks dans testserver/Pal/Content/Paks/~mods/ puis docker restart
```

Critères de succès :
1. le process monte les 24 paks (`ls /proc/<pid>/fd | grep '~mods'`)
2. pas de crash-loop ni d'`OODLE/LZ` error dans les logs
3. REST `/v1/api/info` répond 200
4. une partie se crée (le monde se génère avec les tables moddées)

## Checklist gameplay (partie solo ou serveur de test)

Cocher vite fait, dans l'ordre d'une session naturelle :

| Mod | Vérification (2 min max chacune) |
|---|---|
| BiggerBases | Poser un palbox : construire à ~50 m — accepté (cercle bleu affiché reste 35 m sans pak client) |
| BetterBases | Palbox lv5 → 10 ouvriers max ; blé récolté ×30 ; aucun pal malade/en crise sur la durée |
| CheapBuilding | Mur bois = 1 bois ; pièces qui « snappent » de plus loin |
| CheapCrafting | Établi : coûts ÷5 visibles sur les recettes |
| FeatherStacks (LootComplete non requis) | Poids inventaire ÷2 ; piles de baies à ×2 |
| FastProgress | Labo : une recherche affiche un coût ÷5 ; table d'opération ÷5 |
| PalShopPimped | Marchand de pals (village désert) : légendaires au catalogue ≤ lv50 |
| ItemShopPimped | Boutique village : sphère Tera 15 000, pierre IV 30 000 |
| GTAPalpagos | Voler un objet devant un PNJ : wanted, prime affichée ×20 |
| LootComplete | Tuer un alpha : schematic légendaire garantie ; coffre Grade2+ : parfois une légendaire |
| WildSpawns | Plaine de départ : que des Depresso 🪳 ; Sky Island : légendaires sauvages |
| PalStats | Un boss de donjon a ~4× ses HP ; les pals transportent visiblement plus vite |
| EarlyLearner | Un pal fraîchement capturé : attaques débloquées à des niveaux ÷2 |
| CombatPlus | Cooldowns d'attaques plus courts en combat |
| ExpressFriendship | Rang d'amitié qui monte vite |
| LightningExpeditions (via LootComplete) | Expédition : 3 min au lieu de 30 |
| MiracleFishing / PondDeluxe | Pêche : Boss/Nushi nettement plus fréquents |
| RaidJackpot | Après un raid de base : récompenses ×10 |
| MassiveOutbreaks | Un outbreak : ~27 pals au lieu de 9 |
| ArenaChampion | Victoire arène : ×5 récompenses |
| CaptureScholar | Bonus XP de capture ×3 (10 premières captures) |
| DungeonDeluxe | Fins de donjons : coffres hauts grades fréquents |
| CheapStatues | Statue de Pouvoir : 1 relique par rang au début |
| PurePassives | Un pal avec Musclehead : pas de malus craft affiché |

## Test solo (PC Windows, sans serveur)

Les patches datatable s'appliquent aussi en solo (le client est son propre
serveur) : copier le lot dans
`Steam\steamapps\common\Palworld\Pal\Content\Paks\~mods\`, créer une
**nouvelle partie dédiée au test**, dérouler la checklist. Retirer les paks
avant de rejoindre un serveur vanilla.
