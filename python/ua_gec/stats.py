#!/usr/bin/env python3
import argparse
import collections

from functools import cache


class CorpusStatistics:
    """Compute corpus statistics. """

    def __init__(self, corpus):
        self.corpus = corpus
        self.stats = {}
        self.layer = self.corpus.annotation_layer.value
        self.compute()

    def compute(self):
        all_docs = self.corpus.get_documents()  # annotated by all annotators
        docs = [doc for doc in all_docs if doc.meta.annotator_id == 1]  # unique source docs

        self.stats["Total"] = {}
        self.stats["Total"]["All"] = self._subset_stats(docs)
        self.stats["By gender"] = self._breakdown(docs, "gender")
        self.stats["By region"] = self._breakdown(docs, "region")
        self.stats["By native"] = self._breakdown(docs, "is_native")
        self.stats["By occupation"] = self._breakdown(docs, "occupation")
        self.stats["By submission type"] = self._breakdown(docs, "submission_type")
        self.stats["By translation lang"] = self._breakdown(docs, "source_language")
        self.stats["Number of errors (by 2 annotators)"] = self._count_errors(all_docs)
        del self.stats['By translation lang']['']

    def _subset_stats(self, docs):
        stats = {}
        stats["Documents"] = len(docs)
        stats["Sentences"] = sum(self.count_source_sentences(doc) for doc in docs)
        stats["Tokens"] = sum(self.count_tokens(doc) for doc in docs)
        stats["Unique users"] = len(set(doc.meta.author_id for doc in docs))

        return stats

    def reset_stats(self):
        pass

    def pretty_print(self):
        for top_key, subset in sorted(self.stats.items()):
            print(f"# {top_key}")
            for key, value in subset.items():
                print(f"{key:<30} {value}")
            print()

    @cache
    def count_source_sentences(self, doc):
        return len(doc.source_sentences)

    @cache
    def count_tokens(self, doc):
        return sum(len(s.split()) for s in doc.source_sentences_tokenized)

    def _breakdown(self, docs, field):
        """Compute statistics with breakdown by `field`.

        Returns:
            dict: field_class (str) => stats (dict[str, int])
        """

        result = {}
        values = sorted({getattr(doc.meta, field) for doc in docs})

        for value in values:
            subset = [doc for doc in docs if getattr(doc.meta, field) == value]
            result[value] = self._subset_stats(subset)

        return result
    
    def _count_errors(self, docs):
        """Compute number of error annotations in the given docs. """

        errors = collections.Counter()
        for doc in docs:
            for ann in doc.annotated.get_annotations():
                try:
                    errors[ann.meta["error_type"]] += 1
                except KeyError:
                    print(doc.doc_id)
                    print(ann)
                    errors["MISSING"] += 1
                    #raise
                    continue
                errors["TOTAL"] += 1
        return dict(sorted(errors.items()))


def main(args):
    from ua_gec import Corpus
    corpus = Corpus(args.partition, args.layer)
    stats = CorpusStatistics(corpus)
    stats.pretty_print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("partition", choices=["all", "train", "test"])
    parser.add_argument("layer", choices=["gec-fluency", "gec-only"])
    args = parser.parse_args()
    main(args)
