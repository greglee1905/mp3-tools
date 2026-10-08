import argparse
import re
from pathlib import Path

import mutagen
from mutagen.id3 import APIC, TALB, TIT2, TPE1, TPE2, PictureType

from utils import setup_logger

AUDIO_EXTENSIONS = {".mp3", ".wav", ".aif", ".aiff"}
ARTWORK_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}

logger = setup_logger("tag_album")


def clean_title(stem: str, artist: str) -> str:
    """Derive a track title from a filename stem.

    Strips a leading "Artist - " prefix and normalises whitespace,
    e.g. "Raid ( Rene Wise Reassembly )" -> "Raid (Rene Wise Reassembly)".
    """
    title = stem
    prefix = f"{artist} - "
    if title.lower().startswith(prefix.lower()):
        title = title[len(prefix):]
    title = re.sub(r"\(\s+", "(", title)
    title = re.sub(r"\s+\)", ")", title)
    title = re.sub(r"\[\s+", "[", title)
    title = re.sub(r"\s+\]", "]", title)
    return re.sub(r"\s+", " ", title).strip()


def safe_filename(name: str) -> str:
    return re.sub(r'[/\\:*?"<>|]', "-", name)


def tag_file(path: Path, artist: str, album: str, title: str, artwork: tuple[bytes, str] | None) -> None:
    audio = mutagen.File(path)
    if audio is None:
        raise ValueError(f"Unsupported or unreadable file: {path}")
    if audio.tags is None:
        audio.add_tags()

    tags = audio.tags
    tags.setall("TPE1", [TPE1(encoding=3, text=artist)])
    tags.setall("TPE2", [TPE2(encoding=3, text=artist)])
    tags.setall("TALB", [TALB(encoding=3, text=album)])
    tags.setall("TIT2", [TIT2(encoding=3, text=title)])
    if artwork:
        data, mime = artwork
        tags.delall("APIC")
        tags.add(APIC(encoding=3, mime=mime, type=PictureType.COVER_FRONT, desc="Cover", data=data))

    # ID3v2.3 for best compatibility with DJ software (Rekordbox, Serato, etc.)
    audio.save(v2_version=3)


def main(folder: Path, artist: str, album: str, artwork_path: Path | None, dry_run: bool) -> None:
    if not folder.is_dir():
        raise SystemExit(f"Not a directory: {folder}")

    artwork = None
    if artwork_path:
        mime = ARTWORK_MIME.get(artwork_path.suffix.lower())
        if mime is None:
            raise SystemExit(f"Artwork must be one of {sorted(ARTWORK_MIME)}: {artwork_path}")
        artwork = (artwork_path.read_bytes(), mime)

    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS)
    logger.info(f"Found {len(files)} audio files in {folder}")

    for path in files:
        title = clean_title(path.stem, artist)
        target = path.with_name(safe_filename(f"{artist} - {title}") + path.suffix)

        if target != path and target.exists():
            logger.warning(f"Skipping {path.name}: {target.name} already exists")
            continue

        logger.info(f"{path.name} -> {target.name} | title='{title}'")
        if dry_run:
            continue

        tag_file(path, artist, album, title, artwork)
        if target != path:
            path.rename(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename to 'Artist - Title.ext' and set ID3 tags for an album folder.")
    parser.add_argument("--path", "-p", type=Path, required=True, help="Folder containing the album's audio files.")
    parser.add_argument("--artist", "-a", required=True, help="Artist name (also used as album artist).")
    parser.add_argument("--album", "-l", required=True, help="Album name.")
    parser.add_argument("--artwork", "-c", type=Path, help="Cover image (.jpg/.jpeg/.png).")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show changes without writing.")
    args = parser.parse_args()
    main(args.path, args.artist, args.album, args.artwork, args.dry_run)
