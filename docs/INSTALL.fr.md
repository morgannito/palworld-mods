*[English version](INSTALL.md)*

# Installer les mods — pas à pas

Ce sont des mods **server-side** : ils s'installent uniquement sur le
serveur. Les joueurs (Steam, Xbox, PS5, Mac en crossplay) n'installent rien
et en profitent automatiquement.

## 1. Télécharger

Récupère les `.pak` voulus dans la
[dernière release](https://github.com/morgannito/palworld-mods/releases/latest).
Un pak = un mod — le [tableau des mods](../README.fr.md) décrit chacun.

**Règle d'or : un seul pak par table du jeu.** Certains mods éditent la même
table et s'écraseraient entre eux. C'est le rôle des paks combinés :

| Au lieu de charger… | Charge ce pak unique |
|---|---|
| JackpotChests + LightningExpeditions + BoostedRelics + ElementalDrops + GenerousAlphas | `LootComplete_P.pak` |
| DepressoWorld + LegendarySafari + DungeonRoulette + NightTerrors | `WildSpawns_P.pak` |
| EpicBosses + FastHaulers + TowerTitans | `PalStats_P.pak` |

Tout le reste se combine librement.

## 2. Installer (selon ton setup)

### Serveur dédié Linux (auto-hébergé)

```sh
mkdir -p ~/Steam/steamapps/common/PalServer/Pal/Content/Paks/~mods
cp *.pak ~/Steam/steamapps/common/PalServer/Pal/Content/Paks/~mods/
# si le serveur tourne sous son propre user :
chown -R palworld:palworld ~/Steam/steamapps/common/PalServer/Pal/Content/Paks/~mods
# puis restart (systemctl restart palworld, ou ta méthode habituelle)
```

### Docker (ex. thijsvanloef/palworld-server-docker)

Copie les paks dans le volume monté, sous
`<ton-volume>/Pal/Content/Paks/~mods/` (crée le dossier), puis
`docker restart <conteneur>`.

### Hébergeur loué (Nitrado, G-Portal…)

Connecte-toi en FTP/SFTP depuis le panel et dépose les paks dans
`.../PalServer/Pal/Content/Paks/~mods/` (crée le dossier `~mods` — le nom
compte, tilde inclus). Restart depuis le panel.

⚠️ Certains hébergeurs purgent les fichiers inconnus lors des mises à jour.
Si tes mods disparaissent après une MAJ du jeu, re-dépose-les.

### Serveur dédié Windows

Dépose les paks dans
`steamapps\common\PalServer\Pal\Content\Paks\~mods\` et restart.

### Solo / coop sans serveur dédié

Les mêmes paks marchent en solo (ton jeu fait office de serveur) :
`steamapps\common\Palworld\Pal\Content\Paks\~mods\`.
Utilise un monde de test dédié, et retire les paks avant de rejoindre des
serveurs vanilla qui ne sont pas à toi.

## 3. Vérifier que ça marche

Les checks les plus rapides en jeu après restart :

- **CheapCrafting** : ouvre un établi — coûts de recettes ÷5
- **BiggerBases** : tu peux construire à ~70 m du Palbox (le cercle bleu
  affiche toujours 35 m — purement visuel)
- **GTAPalpagos** : vole un objet au village — prime ×20

Sur Linux, tu peux aussi confirmer que le serveur a monté les paks :

```sh
PID=$(pgrep -f PalServer-Linux | head -1)
ls -l /proc/$PID/fd | grep -c '~mods'   # ≈ nombre de paks chargés
```

## 4. Désinstaller / rollback

Supprime le(s) pak(s) de `~mods/` et restart. Les saves ne sont pas touchées
— ces mods changent les règles du jeu, pas les données de ton monde. (Les
pals obtenus grâce à un mod — ex. légendaires du safari — restent à toi.)

## FAQ

**Une MAJ du jeu vient de sortir et tout semble vanilla/cassé.**
Des paks bâtis sur les anciennes tables écrasent les nouveautés de la MAJ.
Retire-les, attends une release rebuilée (ou rebuild toi-même :
`scripts/update.sh`), puis réinstalle.

**Les joueurs doivent-ils avoir la même version que le serveur ?**
La même version du *jeu* (Steam gère), mais jamais les mods eux-mêmes.

**Les joueurs console peuvent-ils rejoindre ?**
Oui — server-side only, le crossplay n'est pas affecté.

**Ça ne fait rien.**
Vérifie que le dossier s'appelle exactement `~mods` (avec le tilde), dans
`Pal/Content/Paks/`, et que tu as bien restart. Vérifie aussi que tu n'as pas
chargé deux paks qui éditent la même table (tableau des combinés ci-dessus).

**C'est autorisé ?**
Modder son propre serveur suit la même pratique communautaire que les mods
Nexus/CurseForge. N'utilise pas de mods sur un serveur qui n'est pas à toi
sans l'accord du proprio.
