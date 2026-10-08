
MP3_PATH += "/Users/greglee/tunes/licensed_music/collection/2026/"

my-tag-to-genre:
	@echo "--- Copying tag to genre field ---"
	python3 my_tag_to_genre.py -p "$(MP3_PATH)"

# Usage: make tag-album FOLDER="..." ARTIST="..." ALBUM="..." [ARTWORK="cover.jpg"] [DRY_RUN=1]
tag-album:
	@test -n "$(FOLDER)" -a -n "$(ARTIST)" -a -n "$(ALBUM)" || \
		(echo 'Usage: make tag-album FOLDER="..." ARTIST="..." ALBUM="..." [ARTWORK="cover.jpg"] [DRY_RUN=1]'; exit 1)
	@echo "--- Renaming and tagging $(FOLDER) ---"
	uv run python tag_album.py -p "$(FOLDER)" -a "$(ARTIST)" -l "$(ALBUM)" \
		$(if $(ARTWORK),-c "$(ARTWORK)") $(if $(DRY_RUN),--dry-run)