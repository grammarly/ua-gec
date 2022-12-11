#!/usr/bin/env python3
"""Make an M2 file for a given corpus partition/layer.

M2 specifics:
- Annotations are done on a sentence level.
- Texts are tokenized with Stanza.
- The error type annotations are lost (might be added later).
- There's a special document heading sentence added to the beginning of each
  document. It looks like this: `# 0123` (where `0123` is the document ID).
  This adds opportunity to utilize document-level context.
"""
import argparse
import re
import subprocess
from io import StringIO

import errant
import ua_gec
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", choices=["test", "train", "all"], required=True)
    parser.add_argument("--layer", type=ua_gec.AnnotationLayer, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    corpus = ua_gec.Corpus(args.partition, args.layer)
    make_m2(corpus, args.output)


def make_m2(corpus, output_path):
    errant_ = errant.load("en")
    doc_ids = sorted({doc.doc_id for doc in corpus})
    result = []
    for doc_id in tqdm(doc_ids):
        source = corpus.get_doc(doc_id).source_sentences_tokenized
        targets = []
        for annotator in (1, 2):
            try:
                doc = corpus.get_doc(doc_id, annotator_id=annotator)
                targets.append(doc.target_sentences_tokenized)
            except LookupError:
                pass

        m2 = annotate(errant_, source, targets)
        result.append(m2_doc_heading(doc_id))
        result.append(m2)

    m2 = "".join(result)
    m2 = remove_error_types(m2)

    with open(output_path, "wt") as f:
        f.write(m2)


def annotate(annotator, source, targets, merging="rules"):
    out_m2 = StringIO("wt")
    in_files = [source] + targets
    for line in zip(*in_files):
        orig = line[0].strip()
        cors = line[1:]
        if not orig:
            continue
        orig = annotator.parse(orig)
        out_m2.write(" ".join(["S"] + [token.text for token in orig]) + "\n")

        # Loop through the corrected texts
        for cor_id, cor in enumerate(cors):
            cor = cor.strip()
            # If the texts are the same, write a noop edit
            if orig.text.strip() == cor:
                out_m2.write(noop_edit(cor_id) + "\n")
            # Otherwise, do extra processing
            else:
                cor = annotator.parse(cor)
                # Align the texts and extract and classify the edits
                edits = annotator.annotate(orig, cor, merging=merging)
                # Loop through the edits
                for edit in edits:
                    # Write the edit to the output m2 file
                    out_m2.write(edit.to_m2(cor_id) + "\n")
        # Write a newline when we have processed all corrections for each line
        out_m2.write("\n")

    return out_m2.getvalue()


def remove_error_types(m2):
    # Errant's error type classifier is not applicable to Ukrainian.
    # Remove the error type annotations, but leave the first letter of it
    # (R - Replacement, M - Missing, U - unnecessary)
    return re.sub(r"\|\|\|([A-Z]):[A-Z]+\|\|\|", r"|||\1|||", m2)


def noop_edit(annotator_id=0):
    return f"A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||{annotator_id}"


def m2_doc_heading(doc_id):
    return f"""\
S # {doc_id}
A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0

"""


if __name__ == "__main__":
    main()
