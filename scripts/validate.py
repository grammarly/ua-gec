#!/usr/bin/env python3
"""Validate data for consistency.
"""

from collections import defaultdict
from ua_gec import Corpus



def check_files_without_annotations(corpus):
    missing_by_partition = defaultdict(list)
    for doc in corpus:
        if not doc.annotated.get_annotations():
            part = doc.meta.partition
            missing_by_partition[part].append(doc.doc_id)

    if missing_by_partition:
        for part, doc_ids in missing_by_partition.items():
            print(f"Annotations missing in the {part}:")
            print("\n".join(doc_ids))
            print()

    return not missing_by_partition



def main():
    corpus = Corpus("all")

    check_files_without_annotations(corpus)

if __name__ == "__main__":
    main()
