#!/usr/bin/env bash
# update.sh — workflow complet après une MAJ de Palworld :
#   1. ré-extrait gamedata/ depuis le pak du serveur (SSH, lecture seule)
#   2. rafraîchit le .usmap depuis PalworldModding/UsefulFiles (master)
#   3. rebuilde tous les mods (cache invalidé automatiquement par mtime)
#   4. verify.py sur tous les paks — le rapport dit ce que la MAJ a cassé
#
# Usage : scripts/update.sh [--dry-run] [--skip-extract]
set -euo pipefail

SSH_HOST="${PALWORLD_SSH_HOST:-morgannriu}"
REMOTE_PAK="/home/palworld/server/Pal/Content/Paks/Pal-LinuxServer.pak"
REMOTE_TMP="/tmp/palmod-update"
REPAK_URL="https://github.com/trumank/repak/releases/download/v0.2.3/repak_cli-x86_64-unknown-linux-gnu.tar.xz"
USMAP_URL="https://raw.githubusercontent.com/PalworldModding/UsefulFiles/master/Mappings.usmap"
INCLUDES=(
  "Pal/Content/Pal/DataTable/**"
  "Pal/Content/Pal/Blueprint/System/BP_PalGameSetting.*"
  "Pal/Content/Pal/Blueprint/MapObject/BuildObject/**"
  "Pal/Content/Others/nakano_test/**"
)

cd "$(dirname "$0")/.."
DRY=0; SKIP_EXTRACT=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --skip-extract) SKIP_EXTRACT=1 ;;
    *) echo "arg inconnu: $a" >&2; exit 2 ;;
  esac
done

run() { if [ "$DRY" = 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }

echo "== 1/4 extraction gamedata depuis $SSH_HOST"
if [ "$SKIP_EXTRACT" = 0 ]; then
  INC=""; for i in "${INCLUDES[@]}"; do INC="$INC --include \"$i\""; done
  run ssh "$SSH_HOST" "mkdir -p $REMOTE_TMP && cd $REMOTE_TMP \
    && ([ -x ./repak ] || (curl -sL $REPAK_URL | tar xJ --strip-components=1)) \
    && sudo ./repak unpack $INC --output $REMOTE_TMP/extract $REMOTE_PAK \
    && tar czf gamedata.tar.gz -C extract . && rm -rf extract"
  run scp -q "$SSH_HOST:$REMOTE_TMP/gamedata.tar.gz" /tmp/palmods-gamedata.tar.gz
  if [ "$DRY" = 0 ]; then
    rm -rf gamedata
    mkdir -p gamedata
    tar xzf /tmp/palmods-gamedata.tar.gz -C gamedata
    echo "   gamedata/ remplacé ($(find gamedata -name '*.uasset' | wc -l | tr -d ' ') assets)"
  fi
else
  echo "   (sauté)"
fi

echo "== 2/4 mise à jour du usmap"
run curl -sL "$USMAP_URL" -o mappings/Mappings.usmap
echo "   ⚠ vérifier que le repo mappings a bien été mis à jour pour la nouvelle"
echo "     version du jeu (https://github.com/PalworldModding/UsefulFiles/commits)"

echo "== 3/4 rebuild de tous les mods"
run python3 scripts/build.py

echo "== 4/4 vérification end-to-end"
run python3 scripts/verify.py

echo "OK — si des mods échouent en verify, la MAJ a changé leurs tables :"
echo "     diff les nouveaux JSON (build/json-cache) et adapter les patch.py."
