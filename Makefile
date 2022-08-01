.PHONY: install stats postprocess


install:
	cd python && python setup.py develop

stats:
	./python/ua_gec/stats.py all | tee stats.txt

postprocess:
	rm -rf data/gec-*/test/source*
	rm -rf data/gec-*/test/target*
	rm -rf data/gec-*/train/source*
	rm -rf data/gec-*/train/target*
	./scripts/postprocess_dataset.py --annotation-type gec-fluency
	./scripts/postprocess_dataset.py --annotation-type gec-only
