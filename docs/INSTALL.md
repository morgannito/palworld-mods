*[Version française](INSTALL.fr.md)*

# Installing the mods — step by step

These are **server-side** mods: you install them on the server only. Players
(Steam, Xbox, PS5, Mac via crossplay) don't install anything and benefit
automatically.

## 1. Download

Grab the `.pak` files you want from the
[latest release](https://github.com/morgannito/palworld-mods/releases/latest).
Each pak is one mod — the [mod table](../README.md#the-mods) says what each
one does.

**Golden rule: one pak per game table.** Some mods edit the same table and
would overwrite each other. That's what the combined paks are for:

| Instead of loading… | Load this single pak |
|---|---|
| JackpotChests + LightningExpeditions + BoostedRelics + ElementalDrops + GenerousAlphas | `LootComplete_P.pak` |
| DepressoWorld + LegendarySafari + DungeonRoulette + NightTerrors | `WildSpawns_P.pak` |
| EpicBosses + FastHaulers + TowerTitans | `PalStats_P.pak` |

Everything else can be mixed freely.

## 2. Install (pick your setup)

### Linux dedicated server (self-hosted)

```sh
mkdir -p ~/Steam/steamapps/common/PalServer/Pal/Content/Paks/~mods
cp *.pak ~/Steam/steamapps/common/PalServer/Pal/Content/Paks/~mods/
# if the server runs under its own user:
chown -R palworld:palworld ~/Steam/steamapps/common/PalServer/Pal/Content/Paks/~mods
# then restart the server (systemctl restart palworld, or your usual way)
```

### Docker (e.g. thijsvanloef/palworld-server-docker)

Copy the paks into the mounted volume, under
`<your-volume>/Pal/Content/Paks/~mods/` (create the folder), then
`docker restart <container>`.

### Rented host (Nitrado, G-Portal, etc.)

Connect with FTP/SFTP from your host's panel and upload the paks to
`.../PalServer/Pal/Content/Paks/~mods/` (create the `~mods` folder — the name
matters, tilde included). Restart the server from the panel.

⚠️ Keep local copies of your paks: SteamCMD's `validate` leaves the `~mods`
folder alone (it's outside Steam's manifest), but some host panels do full
reinstalls on game updates. If your mods vanish after an update, re-upload —
after checking they've been rebuilt for the new game version.

### Windows dedicated server

Drop the paks into
`steamapps\common\PalServer\Pal\Content\Paks\~mods\` and restart.

### Solo / co-op without a dedicated server

The same paks work in singleplayer (your game acts as the server):
`steamapps\common\Palworld\Pal\Content\Paks\~mods\`.
Use a dedicated test world, and remove the paks before joining vanilla
servers you don't own.

## 3. Check it works

Fastest in-game checks after restart:

- **CheapCrafting**: open a workbench — recipe costs are ÷5
- **BiggerBases**: you can build ~70 m from the Palbox (the blue circle still
  displays 35 m — that's visual only)
- **GTAPalpagos**: steal in a village — the bounty is ×20

On Linux you can also confirm the server actually mounted the paks:

```sh
PID=$(pgrep -f PalServer-Linux | head -1)
ls -l /proc/$PID/fd | grep -c '~mods'   # ≈ number of loaded paks
```

## 4. Uninstall / rollback

Delete the pak(s) from `~mods/` and restart. These mods don't write to your
save files and add no new entities (only vanilla values and references), so
removal is designed to be safe — pals or items obtained thanks to a mod stay
yours. That said, **back up `Pal/Saved/` before any change**: it's the
standard practice the community and Pocketpair recommend around mods.

## FAQ

**A game update just dropped and things look vanilla/broken.**
Paks built on old tables override the update's changes and may misbehave.
Remove them, wait for a rebuilt release (or rebuild yourself:
`scripts/update.sh`), then re-install.

**A MAJOR game update is coming (like 1.0 was).**
Follow [Pocketpair's official guidance](https://www.pcgamer.com/games/survival-crafting/palworld-studio-says-delete-your-old-mods-before-the-1-0-release-disabling-them-is-not-enough/):
**delete** mods before updating ("disabling them is not enough"), back up
saves, update clean, then re-install rebuilt mods. Major updates can run save
conversions — you want those to happen on vanilla data.

**Do players need the same version as the server?**
They need the same *game* version as the server (Steam handles that), but
never the mods themselves.

**Can console players join?**
Yes — server-side only, crossplay unaffected.

**It does nothing.**
Check the folder is exactly `~mods` (with the tilde), inside
`Pal/Content/Paks/`, and that you restarted the server. Check you didn't load
two paks that edit the same table (see the combined paks table above).

**Is this allowed?**
Server-side modding of your own server follows the same community practice as
Nexus/CurseForge mods. Don't use mods on servers you don't own without the
owner's consent.
