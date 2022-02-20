#!/usr/bin/env python3
"""Validate data for consistency.
"""

from collections import defaultdict
from ua_gec import Corpus



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
            if ann.meta["error_type"] in ("Grammar", "Fluency"):
                reannotate.add(doc.doc_id)

    if reannotate:
        print(f"{len(reannotate)} docs with missing detailed annotations:")
        #print("\n".join(sorted(reannotate)))


def main():
    corpus = Corpus("all")

    check_files_without_annotations(corpus)
    check_files_with_missing_detailed_annotations(corpus)

if __name__ == "__main__":
    main()
