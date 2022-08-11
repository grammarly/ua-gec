.PHONY: install stats postprocess


install:
	cd python/ua_gec && ln -sf ../../data data
	cd python && python3 setup.py develop

stats:
	./python/ua_gec/stats.py all gec-fluency | tee stats.gec-fluency.txt
	./python/ua_gec/stats.py all gec-only | tee stats.gec-only.txt

postprocess:
	rm -rf data/gec-*/test/source*
	rm -rf data/gec-*/test/target*
	rm -rf data/gec-*/train/source*
	rm -rf data/gec-*/train/target*
	./scripts/postprocess_dataset.py --annotation-layer gec-fluency
	./scripts/postprocess_dataset.py --annotation-layer gec-only
