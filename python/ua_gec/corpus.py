import csv
import collections
import pathlib

from ua_gec.annotated_text import AnnotatedText


Metadata = collections.namedtuple(
    "Metadata",
    "doc_id author_id is_native region gender occupation submission_type "
    "source_language annotator_id partition is_sensitive")


class Document:
    """A single annotated document with metadata. """

    def __init__(self, annotated, meta):
        self._annotated = annotated
        self.meta = meta

    def __str__(self):
        return self.annotated

    def __repr__(self):
        return "<Document(`{}`)>".format(self.annotated)

    @property
    def annotated(self):
        return self._annotated

    @property
    def source(self):
        return self.annotated.get_original_text()

    @property
    def target(self):
        return self.annotated.get_corrected_text()

    @property
    def doc_id(self):
        return self.meta.doc_id


class Corpus:
    """Iterator over documents in the UA-GEC corpus.

    Args:
        partition (str): only look at the selected split if "train" or "test",
            use all corpus if "all". Default is "train".

    Example:

        >>> corpus = Corpus()
        >>> total_chars = sum(len(doc.source) for doc in corpus)
        >>> print(total_chars)
        1493024
    """

    def __init__(self, partition="train"):
        if partition not in ("train", "test", "all"):
            raise ValueError("`partition` must be 'train', 'test' or 'all'")
        self.partition = partition
        self.annotator_id = "1"

        root_dir = pathlib.Path(__file__).parent
        self._data_dir = root_dir / "data"
        self._metadata = None
        self._docs = None  # lazy loaded list of document

    def __repr__(self):
        return "<Corpus(partition={}, len={} docs>".format(
            self.partition, len(self))


    def __str__(self):
        return repr(self)

    def __iter__(self):
        return self.iter_documents()

    def __len__(self):
        return len(self._get_metadata())

    def _get_metadata(self):
        if self._metadata is None:
            self._load_metadata()

        return self._metadata

    def _load_metadata(self):
        self._metadata = []
        reader = csv.DictReader((self._data_dir / "metadata.csv").open())
        for row in reader:
            if self.partition == "all" or row["partition"] == self.partition:
                record = Metadata(
                    doc_id=row["id"],
                    author_id=row["author_id"],
                    is_native=row["is_native"],
                    region=row["region"],
                    gender=row["gender"],
                    occupation=row["occupation"],
                    submission_type=row["submission_type"],
                    source_language=row["source_language"],
                    annotator_id=int(row["annotator_id"]),
                    partition=row['partition'],
                    is_sensitive=bool(row['is_sensitive']),
                )
                self._metadata.append(record)

    def iter_documents(self):
        """Iterate over documents. """

        # Corpus is already loaded
        if self._docs is not None:
            return iter(self._docs)

        # Iterate in a streaming fashion
        for meta in self._get_metadata():
            filename = f"{meta.doc_id}.a{self.annotator_id}.ann"
            path = self._data_dir / meta.partition / "annotated" / filename
            text = AnnotatedText(path.read_text())
            doc = Document(text, meta=meta)
            yield doc

    def get_documents(self):
        """Return a list of all documents in the corpus. """

        if self._docs is None:
            self._docs = list(self.iter_documents())
        return self._docs
    
    def get_doc(self, doc_id):
        """Return one document by its ID.

        Raises LookupError if the document is not found.
        """

        docs = self.get_documents()
        match = [doc for doc in docs if doc.doc_id == doc_id]
        if not match:
            raise LookupError(f"Document {doc_id} not found!")
        
        assert len(match) == 1
        return match[0]
