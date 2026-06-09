#!/usr/bin/env python3
"""Convert source photos to web-optimized WebP (full + thumbnail) for the site.

Reads every HEIC/JPG/JPEG/PNG in the source directory, corrects EXIF
orientation (so portrait shots aren't rendered sideways), writes a full-size
and a thumbnail WebP into assets/img/photos/, and rebuilds manifest.json
(the list the gallery page reads).

Orientation note: macOS `sips` ignores the HEIC orientation flag, which left
portrait shots sideways. Pillow + pillow-heif apply it correctly on every
format, so this replaced the earlier sips/cwebp shell version.

Usage:
    scripts/optimize-photos.py [SOURCE_DIR] [--force]
        SOURCE_DIR   directory of source images (default: ~/Downloads)
        --force      re-convert even if the WebP already exists (default: skip)

Requires:  pip install pillow pillow-heif
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
    import pillow_heif
except ImportError:
    sys.exit("Missing dependencies. Run: pip install pillow pillow-heif")

pillow_heif.register_heif_opener()

SOURCE_EXTS = {".heic", ".jpg", ".jpeg", ".png"}
FULL_MAX = 1800   # longest edge of the full-size image, in px
THUMB_MAX = 480   # longest edge of the thumbnail, in px
Q_FULL = 80
Q_THUMB = 72

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "assets" / "img" / "photos"
THUMB_DIR = OUT_DIR / "thumbs"


def web_optimize(src: Path, force: bool) -> bool:
    """Convert one source image to full + thumbnail WebP. Return True if converted."""
    full_path = OUT_DIR / f"{src.stem}.webp"
    if full_path.exists() and not force:
        return False
    # exif_transpose bakes the orientation into pixels (WebP carries no such tag).
    image = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    _save_webp(image, FULL_MAX, full_path, Q_FULL)
    _save_webp(image, THUMB_MAX, THUMB_DIR / f"{src.stem}.webp", Q_THUMB)
    return True


def _save_webp(image: "Image.Image", max_edge: int, dest: Path, quality: int) -> None:
    """Resize a copy so its longest edge <= max_edge, then write WebP."""
    resized = image.copy()
    resized.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    resized.save(dest, "WEBP", quality=quality, method=6)


def rebuild_manifest() -> int:
    """Rewrite manifest.json as a sorted JSON list of full-size WebP filenames."""
    names = sorted(p.name for p in OUT_DIR.glob("*.webp"))
    (OUT_DIR / "manifest.json").write_text(json.dumps(names, indent=2) + "\n")
    return len(names)


def _convert_logged(src: Path, force: bool) -> bool:
    """Convert one file, printing progress; never raise on a single bad file."""
    try:
        if web_optimize(src, force):
            print(".", end="", flush=True)
            return True
    except Exception as exc:  # one unreadable file shouldn't abort the batch
        print(f"\nFAILED {src.name}: {exc}")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize photos to WebP for the site.")
    parser.add_argument("source", nargs="?", default=str(Path.home() / "Downloads"),
                        help="directory of source images (default: ~/Downloads)")
    parser.add_argument("--force", action="store_true",
                        help="re-convert even if the WebP already exists")
    args = parser.parse_args()

    source_dir = Path(args.source).expanduser()
    if not source_dir.is_dir():
        sys.exit(f"error: source directory not found: {source_dir}")

    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    sources = sorted(p for p in source_dir.iterdir()
                     if p.is_file() and p.suffix.lower() in SOURCE_EXTS)

    converted = sum(_convert_logged(src, args.force) for src in sources)
    total = rebuild_manifest()
    print(f"\nconverted: {converted}   skipped: {len(sources) - converted}   total: {total}")


if __name__ == "__main__":
    main()
