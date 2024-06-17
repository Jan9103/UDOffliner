all: ud.db

clear_cache:
	rm until_idx_*.json

until_idx_0.json:
	# DOWNLOADING UD. this can take several days due to anti-DOS
	python3 ./download_data.py

ud.json: until_idx_0.json
	# merging, sorting, and cleaning data.. this can take a few minutes.
	python3 ./unify.py until_idx_*.json > $@

ud.sqlite3: ud.json
	python3 ./toSqlite.py $< $@ || (rm $@; false)

PHONY: all clear_cache
