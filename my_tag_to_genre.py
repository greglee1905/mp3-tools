
    
import eyed3
import re
import glob
import argparse
from pathlib import Path
from utils import setup_logger

def load_genre_tags(file_path: Path) -> set:
    """Load valid genre tags from a text file.

    :file_path: Path to the text file containing genre tags.
    :returns: Set of genre tags.
    """
    with open(file_path, mode="r", encoding="utf-8") as _file:
        tags = set(_file.read().splitlines())
    return tags


def get_genre_from_tag(file: str, tags: set) -> str:
    """Extract genre from custom tag in comments field of mp3 file.

    :mp3_name: Name of the mp3 file to process.
    :tags: Set of valid genre tags.
    :returns: Genre string if found, else raises Exception.
    """
    my_tag_regex = re.compile(r"(?<=\/\*).*(?=\*\/)")
    
    new_genre_tags = []
    
    if file.tag.genre is None:
        if file.tag.comments is None:
            return None
        elif file.tag.comments[0].text == "":
            return None
        

    if file.tag.genre is not None:
        if file.tag.comments is None:
            return file.tag.genre.name
        elif file.tag.comments[0].text == "":
            return file.tag.genre.name
    
    if file.tag and file.tag.comments:
        # comments is a list-like of CommentFrame objects
        comment_text = file.tag.comments[0].text
        my_tag = my_tag_regex.search(comment_text)
        for tag in my_tag.group().split(" / "): # problem with minimal / deep tech
            tag = tag.strip()
            if tag in tags:
                new_genre_tags.append(tag)

        if len(new_genre_tags) >= 2:
            raise Exception(f"Multiple genre tags found: {new_genre_tags}")
        
    return new_genre_tags[0] if new_genre_tags else None
    


def main(mp3_path: Path, genres_file: Path):

    logger = setup_logger("my_tag_to_genre")

    logger.info(f"Loading genre tags from {genres_file}")
    genre_tags = load_genre_tags(genres_file)

    logger.info(f"Processing mp3 files in {mp3_path}")
    mp3_files = glob.glob(f"{mp3_path}/*.mp3")
    logger.info(f"Found {len(mp3_files)} mp3 files")

    for mp3_path in mp3_files:
        logger.info(f"Processing {mp3_path}")
        if 'Onda' in mp3_path:
            breakpoint()
        file = eyed3.load(mp3_path)
        
        new_genre_tag = get_genre_from_tag(file, genre_tags)
        if new_genre_tag:
            file.tag.genre = eyed3.id3.Genre(new_genre_tag)
            file.tag.save()
        else:
            logger.warning(f"No valid genre tag found in {mp3_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy custom tag to genre field in mp3 files.")
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        help="Path to the directory containing mp3 files."
    )
    parser.add_argument(
        "--genres-file",
        "-g",
        type=Path,
        default="data/genres.txt",
        help="Path to the text file containing valid genre tags."
    )
    args = parser.parse_args()
    main(args.path, args.genres_file)