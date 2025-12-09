
MP3_PATH += "/Users/greglee/tunes/licensed_music/2025/"

my-tag-to-genre:
	@echo "--- Copying tag to genre field ---"
	python3 my_tag_to_genre.py -p "$(MP3_PATH)"