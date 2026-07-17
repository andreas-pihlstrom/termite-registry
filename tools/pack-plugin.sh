#!/bin/bash
# Pack an installed/built plugin folder into a marketplace zip + print its
# sha256. Excludes Frameworks (payloads ship separately) and caches.
#
#   tools/pack-plugin.sh ~/.config/termite/plugins/detox dist/detox-1.0.0.zip
set -euo pipefail
SRC="$1"; OUT="$2"
[ -f "$SRC/manifest.json" ] || { echo "no manifest.json in $SRC" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"
# Code signatures live in file contents. Strip Mac-only resource forks,
# quarantine, ACLs, and extended attributes so shared archives do not contain
# AppleDouble `._*` metadata or inherit the author's quarantine state.
STAGE=$(mktemp -d)
ditto --norsrc --noextattr --noqtn --noacl \
  "$SRC" "$STAGE/$(basename "$SRC")"
rm -rf "$STAGE/$(basename "$SRC")/Frameworks" "$STAGE/$(basename "$SRC")"/*.log
(cd "$STAGE" && ditto -c -k --keepParent --norsrc --noextattr --noqtn --noacl \
  "$(basename "$SRC")" "$OLDPWD/$OUT")
rm -rf "$STAGE"
shasum -a 256 "$OUT" | awk '{print $1}'
