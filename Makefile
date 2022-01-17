.PHONY: install stats postprocess


install:
	cd python && python setup.py develop

stats:
	./python/ua_gec/stats.py all | tee stats.txt

postprocess:
	rm -rf data/test/source*
	rm -rf data/test/target*
	rm -rf data/train/source*
	rm -rf data/train/target*
	./scripts/postprocess_dataset.py
