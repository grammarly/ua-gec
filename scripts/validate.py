#!/usr/bin/env python3
"""Validate data for consistency.
"""

from collections import defaultdict
from ua_gec import Corpus, AnnotationLayer



def check_files_without_annotations(corpus):
    missing_by_partition = defaultdict(list)
    exceptions = ["0460", "0650", "1875", "1880"]
    for doc in corpus:
        if not doc.annotated.get_annotations() and not doc.doc_id in exceptions:
            part = doc.meta.partition
            missing_by_partition[part].append(doc.doc_id)

    if missing_by_partition:
        for part, doc_ids in missing_by_partition.items():
            print(f"Annotations missing in the {part}:")
            print("\n".join(doc_ids))
            print()

    return not missing_by_partition


def check_files_with_missing_detailed_annotations(corpus):
    reannotate = set()
    for doc in corpus:
        for ann in doc.annotated.get_annotations():
            if "error_type" not in ann.meta:
                print(f"Missing error_type in {doc.doc_id}: {ann}")
                continue
            if ann.meta["error_type"] in ("Grammar", "Fluency"):
                reannotate.add(doc.doc_id)

    if reannotate:
        print(f"{len(reannotate)} docs with missing detailed annotations:")
        print(", ".join(sorted(reannotate)))


def check_double_annotated(corpus):
    """Docs with 2 annotators should have exactly the same source. """

    broken = []
    for doc in corpus:
        if doc.meta.annotator_id == 2:
            doc_2 = corpus.get_doc(doc.doc_id, annotator_id=1)
            if doc.source.strip() != doc_2.source.strip():
                broken.append(doc.doc_id)

    if broken:
        print(f"{len(broken)} docs have different source in annotator 1 and annotator 2:")
        print(', '.join(sorted(broken)))


def check_gec_only_and_gec_fluency_source_match():
    """Check that GEC-only and GEC-Fluency has the same number of source sentences. """

    corpus_gec = Corpus("all", annotation_layer=AnnotationLayer.GecOnly)
    corpus_fluency = Corpus("all", annotation_layer=AnnotationLayer.GecAndFluency)

    broken = []
    for doc1, doc2 in zip(corpus_gec, corpus_fluency):
        if doc1.source.strip() != doc2.source.strip():
            broken.append(doc1.doc_id)


    if broken:
        print(f"{len(broken)} docs have different source in GEC-only and GEC-Fluency:")
        print(', '.join(sorted(broken)))


def main():
    corpus = Corpus("all")

    check_files_without_annotations(corpus)
    check_files_with_missing_detailed_annotations(corpus)
    check_double_annotated(corpus)
    check_gec_only_and_gec_fluency_source_match()

if __name__ == "__main__":
    main()
