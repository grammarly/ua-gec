#!/usr/bin/env python3
"""Make an M2 file for a given corpus partition/layer.

M2 specifics:
- Annotations are done on a sentence level.
- Texts are tokenized with Stanza.
- The error types are copied from UA-GEC.
- There's a special document heading sentence added to the beginning of each
  document. It looks like this: `# 0123` (where `0123` is the document ID).
  This adds opportunity to utilize document-level context.
"""
import argparse
import re
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
        doc = corpus.get_doc(doc_id, annotator_id=1)
        edits_1 = get_sentence_edits(errant_, doc)
        try:
            doc = corpus.get_doc(doc_id, annotator_id=2)
            edits_2 = get_sentence_edits(errant_, doc)
        except LookupError:
            edits_2 = None

        m2 = doc_edits_to_m2(doc, edits_1, edits_2)
        result.append(m2)

    m2 = "".join(result)

    with open(output_path, "wt") as f:
        f.write(m2)


def get_sentence_edits(errant_, doc):

    edits_by_sentence = []

    # Maintain mapping from token index in sentence to character index
    #in the document
    doc_index = 0  # character index in the document (source)
    src_text = doc.source
    for src_sent, tgt_sent in zip(doc.source_sentences_tokenized, doc.target_sentences_tokenized):
        src = errant_.parse(src_sent)
        tgt = errant_.parse(tgt_sent)
        edits = errant_.annotate(src, tgt)
        edits_by_token = {}
        insertions_by_token = {}
        for edit in edits:
            for i in range(edit.o_start, edit.o_end):
                edits_by_token[i] = edit
        for edit in edits:
            if edit.o_start == edit.o_end:
                insertions_by_token[edit.o_start] = edit
            
        for token_idx, token in enumerate(src):
            doc_index = src_text.find(token.text, doc_index)
            assert doc_index != -1

            if token_idx in edits_by_token:
                ann = doc.annotated.get_annotation_at(doc_index)
                if ann:
                    error_type = ann.meta['error_type']
                    edit = edits_by_token[token_idx]
                    edit.type = error_type
            if token_idx in insertions_by_token:
                ann = doc.annotated.get_annotation_at(doc_index, doc_index)
                if not ann:
                    ann = doc.annotated.get_annotation_at(doc_index)
                if not ann:
                    ann = doc.annotated.get_annotation_at(doc_index - 1, doc_index - 1)
                if ann:
                    error_type = ann.meta['error_type']
                    edit = insertions_by_token[token_idx]
                    edit.type = error_type
            doc_index += len(token.text)

        edits_by_sentence.append(edits)

    assert len(edits_by_sentence) == len(doc.source_sentences_tokenized)
    return edits_by_sentence



def doc_edits_to_m2(doc, edits_1, edits_2):
    """Convert Errant edits to M2 format.

    Args:
        doc: Document.
        edits_1: List of lists of Errant edits for each sentence in the document.
            Each list is for a different annotator.
        edits_2: List of lists of Errant edits for each sentence in the document.
            Each list is for a different annotator.

    Returns:
        M2 string.
    """
    result = [m2_doc_heading(doc.doc_id)]
    if edits_2 is None:
        edits_2 = ["missing"] * len(edits_1)
     
    for source, s_edits_1, s_edits_2 in zip(
            doc.source_sentences_tokenized, edits_1, edits_2):
        result.append(f"S {source}\n")
        result += _edits_to_m2(s_edits_1, annotator_id=0)
        if s_edits_2 != "missing":
            result += _edits_to_m2(s_edits_2, annotator_id=1)
        result.append("\n")

    return "".join(result)


def _edits_to_m2(edits, annotator_id):
    result = []
    if edits:
        for edit in edits:
            result.append(edit.to_m2(annotator_id) + "\n")
    else:
        result.append(noop_edit(annotator_id) + "\n")
    return result


def noop_edit(annotator_id=0):
    return f"A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||{annotator_id}"


def m2_doc_heading(doc_id):
    return f"""\
S # {doc_id}
A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0
A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||1

"""


if __name__ == "__main__":
    main()
