import pytest
from ua_gec import Corpus, Document, AnnotatedText


class TestCorpus:

    def test_iter_documents(self, corpus):
        doc = next(corpus.iter_documents())

        assert isinstance(doc, Document)
        assert isinstance(doc.annotated, AnnotatedText)
        assert doc.meta.author_id == "34fdde49"

    def test_len(self):
        assert len(Corpus("all")) == len(Corpus("test")) + len(Corpus("train"))

    @pytest.fixture
    def corpus(self):
        return Corpus()
