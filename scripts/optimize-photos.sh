#!/usr/bin/env bash
#
# optimize-photos.sh — convert source photos to web-optimized WebP for the site.
#
# Converts every HEIC/JPG/JPEG/PNG in the source directory into:
#   - a full-size WebP (longest edge capped) in   assets/img/photos/
#   - a thumbnail WebP                       in   assets/img/photos/thumbs/
# then rebuilds assets/img/photos/manifest.json (the list the gallery reads).
#
# Why HEIC -> PNG -> WebP: cwebp can't read HEIC, so sips decodes it first.
# Using a lossless PNG intermediate (not JPEG) avoids double-lossy color loss,
# and sips also bakes in the EXIF rotation so portrait shots aren't sideways.
#
# Usage:
#   scripts/optimize-photos.sh [SOURCE_DIR] [--force]
#     SOURCE_DIR   directory of source images (default: ~/Downloads)
#     --force      re-convert even if the WebP already exists (default: skip)
#
# Requires: sips (macOS, built in) and cwebp (`brew install webp`).

set -euo pipefail

# Resolve the repo root from this script's own location (scripts/ sits at root).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SRC="$HOME/Downloads"
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    *)       SRC="$arg" ;;
  esac
done

OUT="$ROOT/assets/img/photos"
THUMB="$OUT/thumbs"
FULL_MAX=1800   # longest edge of the full-size image, in px
THUMB_W=480     # thumbnail width, in px
Q_FULL=80       # WebP quality for full-size
Q_THUMB=72      # WebP quality for thumbnails

command -v sips  >/dev/null 2>&1 || { echo "error: 'sips' not found (macOS only)."; exit 1; }
command -v cwebp >/dev/null 2>&1 || { echo "error: 'cwebp' not found — run: brew install webp"; exit 1; }
[ -d "$SRC" ] || { echo "error: source directory not found: $SRC"; exit 1; }

mkdir -p "$THUMB"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

converted=0
skipped=0
while IFS= read -r -d '' f; do
  name="$(basename "$f")"; name="${name%.*}"
  if [ "$FORCE" -eq 0 ] && [ -f "$OUT/$name.webp" ]; then
    skipped=$((skipped + 1)); continue
  fi
  if sips -s format png -Z "$FULL_MAX" "$f" --out "$TMP/$name.png" >/dev/null 2>&1; then
    cwebp -quiet -q "$Q_FULL"  "$TMP/$name.png"               -o "$OUT/$name.webp"
    cwebp -quiet -q "$Q_THUMB" -resize "$THUMB_W" 0 "$TMP/$name.png" -o "$THUMB/$name.webp"
    rm -f "$TMP/$name.png"
    converted=$((converted + 1)); printf '.'
  else
    echo "FAILED to decode: $name"
  fi
done < <(find "$SRC" -maxdepth 1 -type f \
          \( -iname '*.heic' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0)
echo

# Rebuild the manifest the gallery page reads (sorted JSON array of filenames).
(
  cd "$OUT"
  printf '[\n'
  ls *.webp 2>/dev/null | sort | sed 's/.*/  "&"/' | sed '$!s/$/,/'
  printf ']\n'
) > "$OUT/manifest.json"

echo "converted: $converted   skipped (already done): $skipped   total: $(ls "$OUT"/*.webp 2>/dev/null | wc -l | tr -d ' ')"
