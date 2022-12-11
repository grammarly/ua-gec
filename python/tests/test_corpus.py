import pytest
from ua_gec import Corpus, Document, AnnotatedText, AnnotationLayer


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
        
    def test_annotation_layer(self):
        corpus_fluency = Corpus(annotation_layer=AnnotationLayer.GecAndFluency)
        corpus_gec = Corpus(annotation_layer=AnnotationLayer.GecOnly)

        doc_fluency = str(corpus_fluency.get_doc("0012").annotated)
        doc_gec = str(corpus_gec.get_doc("0012").annotated)

        s = "число і опис не {співпадають=>збігаються:::error_type=F/Calque}" 
        assert s in doc_fluency
        assert s not in doc_gec

    def test_source_sentences(self):
        corpus = Corpus("test")
        doc = corpus.get_doc("1224")
        assert isinstance(doc.source_sentences, list)
        assert len(doc.source_sentences) == 6

    def test_source_sentences_tokenized(self):
        corpus = Corpus("test")
        doc = corpus.get_doc("1224")
        assert isinstance(doc.source_sentences_tokenized, list)
        assert len(doc.source_sentences_tokenized) == 6
        assert doc.source_sentences_tokenized[0] == "Шон Байзель ."

    def test_target_sentences(self):
        corpus = Corpus("test")
        doc_a1 = corpus.get_doc("1224", annotator_id=1)
        doc_a2 = corpus.get_doc("1224", annotator_id=2)
        assert isinstance(doc_a1.target_sentences, list)
        assert doc_a1.target_sentences != doc_a2.target_sentences

    @pytest.fixture
    def corpus(self):
        return Corpus()
