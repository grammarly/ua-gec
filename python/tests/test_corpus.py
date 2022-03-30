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

    def test_get_doc(self, corpus):
        assert corpus.get_doc("0042").meta.doc_id == "0042"

    def test_get_doc_not_exists(self, corpus):
        assert corpus.get_doc("0042").meta.doc_id == "0042"

        with pytest.raises(LookupError):
            corpus.get_doc("THIS ID DOSN'T EXISTS")

    def test_two_annotators(self):
        corpus = Corpus("test")
        doc_a1 = corpus.get_doc("1224", annotator_id=1)
        doc_a2 = corpus.get_doc("1224", annotator_id=2)

        assert doc_a1.doc_id == doc_a2.doc_id == "1224"
        assert doc_a1.target != doc_a2.target


    @pytest.fixture
    def corpus(self):
        return Corpus()
