#!/usr/bin/env bash
# deploy.sh — déploiement d'un lot de paks sur le serveur, avec filet complet.
#
# JAMAIS exécuté automatiquement : exige DEPLOY=yes dans l'environnement.
#
#   DEPLOY=yes scripts/deploy.sh dist/BetterBases_P.pak dist/BiggerBases_P.pak
#   DEPLOY=yes scripts/deploy.sh --replace dist/*.pak   # vide ~mods d'abord
#
# Étapes : verify.py sur le lot → scp → sauvegarde de ~mods → install+chown →
# restart sûr (palworld-restart.sh : backup save + gardes) → contrôle REST +
# paks réellement montés par le process → rollback automatique si échec.
set -euo pipefail

SSH_HOST="${PALWORLD_SSH_HOST:-morgannriu}"
MODS_DIR="/home/palworld/server/Pal/Content/Paks/~mods"
RESTART="/usr/local/bin/palworld-restart.sh"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="/var/backups/palworld-mods-$STAMP"

cd "$(dirname "$0")/.."

[ "${DEPLOY:-}" = "yes" ] || { echo "refus : lancer avec DEPLOY=yes (déploiement = décision explicite)"; exit 1; }

REPLACE=0
PAKS=()
for a in "$@"; do
  case "$a" in
    --replace) REPLACE=1 ;;
    *.pak) PAKS+=("$a") ;;
    *) echo "arg inconnu: $a" >&2; exit 2 ;;
  esac
done
[ "${#PAKS[@]}" -gt 0 ] || { echo "usage: DEPLOY=yes $0 [--replace] dist/X_P.pak ..."; exit 2; }

echo "== verify local du lot"
python3 scripts/verify.py $(basename -s .pak "${PAKS[@]}" | sed 's/$//')

echo "== conflits de tables dans le lot"
python3 - "${PAKS[@]}" <<'PYEOF'
import subprocess, sys
from pathlib import Path
from collections import defaultdict
repak = Path.home() / ".cargo" / "bin" / "repak"
by_table = defaultdict(list)
for pak in sys.argv[1:]:
    out = subprocess.run([str(repak), "list", pak], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.endswith(".uasset"):
            by_table[line].append(Path(pak).name)
dupes = {t: p for t, p in by_table.items() if len(p) > 1}
if dupes:
    for t, p in dupes.items():
        print(f"CONFLIT : {t} présent dans {p}")
    sys.exit(1)
print("aucun conflit dans le lot")
PYEOF

echo "== transfert"
scp -q "${PAKS[@]}" "$SSH_HOST:/tmp/"

NAMES=$(for p in "${PAKS[@]}"; do basename "$p"; done)
echo "== sauvegarde + install + restart (rollback auto si échec)"
ssh "$SSH_HOST" bash -s <<EOF
set -euo pipefail
sudo mkdir -p "$BACKUP"
sudo cp -a "$MODS_DIR/." "$BACKUP/" 2>/dev/null || true
if [ "$REPLACE" = 1 ]; then sudo find "$MODS_DIR" -mindepth 1 -name '*.pak' -delete; fi
for n in $NAMES; do sudo mv "/tmp/\$n" "$MODS_DIR/\$n"; done
sudo chown -R palworld:palworld "$MODS_DIR"

if sudo "$RESTART"; then
  sleep 5
  PID=\$(pgrep -f PalServer-Linux-Shipping | head -1)
  MOUNTED=\$(sudo ls -l /proc/\$PID/fd 2>/dev/null | grep -c '~mods' || true)
  echo "paks montés par le process : \$MOUNTED"
  PW=\$(sudo grep -oP 'AdminPassword="\\K[^"]+' /home/palworld/server/Pal/Saved/Config/LinuxServer/PalWorldSettings.ini)
  curl -sf -u admin:\$PW http://localhost:8212/v1/api/info >/dev/null && echo "REST OK" || { echo "REST KO"; exit 1; }
else
  echo "RESTART EN ÉCHEC — ROLLBACK"
  sudo find "$MODS_DIR" -mindepth 1 -name '*.pak' -delete
  sudo cp -a "$BACKUP/." "$MODS_DIR/" 2>/dev/null || true
  sudo chown -R palworld:palworld "$MODS_DIR"
  sudo "$RESTART"
  exit 1
fi
EOF

echo "OK — déployé. Rollback manuel si besoin : restaurer $BACKUP puis restart."
