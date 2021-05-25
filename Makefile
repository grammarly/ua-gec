.PHONY: install stats tokenize


install:
	cd python && python setup.py develop

stats:
	./python/ua_gec/stats.py all | tee stats.txt

tokenize:
	rm -rf data/{train,test}/*-sentences
	./scripts/sentencize.py
