#!/usr/bin/env python3
"""This script produces the following postprocessed views of an annotated dataset:

1. `./source` -- the source (errorful) side of text (annotations stripped)
2. `./target` -- the target (corrected) side of target (annotations stripped)
3. `./source-sentences` -- the source side split into sentences
4. `./target-sentences` -- same for target
5. `./source-sentences-tokenized` -- the source side split into sentences and tokenized
6. `./target-sentences-tokenized` -- same for target.

All these views originate in `./annotated` which should be considered as the
source of truth.

"""

import argparse
from pathlib import Path

import stanza
import tqdm
import ua_gec
from pyxdameraulevenshtein import damerau_levenshtein_distance


def main(data_dir="./data", annotation_layer="gec-only"):
    annotation_layer = ua_gec.AnnotationLayer(annotation_layer)
    data_dir = Path(data_dir) / annotation_layer.value
    for partition in ("train", "test"):
        out_dir = data_dir / partition
        print(f"~~~ Preprocess {partition} partition to {out_dir}")
        corpus = ua_gec.Corpus(partition, annotation_layer=annotation_layer)
        do_partition(out_dir, corpus)


def do_partition(out_dir, corpus):

    for doc in tqdm.tqdm(corpus.get_documents()):

        src = split_sentences(doc.source)
        tgt = split_sentences(doc.target)
        output_src, output_tgt = align_sentences(src, tgt)
        fname_src = f"{doc.doc_id}.src.txt"
        fname_tgt = f"{doc.doc_id}.a{doc.meta.annotator_id}.txt"

        # Write source-only and target-only docs (with no annotations)
        path_src = out_dir / "source" / fname_src
        path_tgt = out_dir / "target" / fname_tgt
        path_src.parent.mkdir(exist_ok=True)
        path_tgt.parent.mkdir(exist_ok=True)
        path_src.write_text(doc.source)
        path_tgt.write_text(doc.target)

        # Write sentence-level documents
        path_src = out_dir / "source-sentences" / fname_src
        path_tgt = out_dir / "target-sentences" / fname_tgt
        path_src.parent.mkdir(exist_ok=True)
        path_tgt.parent.mkdir(exist_ok=True)
        path_src.write_text("\n".join(output_src))
        path_tgt.write_text("\n".join(output_tgt))

    for iteration in range(1, 4):
        num_affected = 0
        num_affected += _realign_corpus_sentences_1(out_dir, corpus)
        num_affected += _realign_corpus_sentences_2(out_dir, corpus)
        #print(f"Iter {iteration}: realigned {num_affected} docs")
        if num_affected == 0:
            # May need a couple of iterations
            break
    else:
        print(f"WARNING: Realign didn't converge for {corpus}")

    _tokenize_corpus(out_dir, corpus)


def _realign_corpus_sentences_1(out_dir, corpus):
    """Fix sentence alignment for trailing newlines. """

    # Sometimes, the list of sentences may include newlines.
    # For example, a source sentence consists of a quotation mark,
    # and the target removes that, so the sentence is an empty line.
    # We need to realign these cases, but realign target to source.

    num_affected = 0
    for doc in tqdm.tqdm(corpus.get_documents()):
        a = doc.meta.annotator_id
        path_src = out_dir / "source-sentences" / f"{doc.doc_id}.src.txt"
        path_tgt = out_dir / "target-sentences" / f"{doc.doc_id}.a{a}.txt"

        src = path_src.read_text().split("\n")
        tgt = path_tgt.read_text().strip().split("\n")

        if len(src) == len(tgt):
            continue  # no problem here

        print(f"Realigning {doc.doc_id} (a{a})")
        print(f"  old: {len(src)} -> {len(tgt)}")
        tgt, src = align_sentences(tgt, src)
        path_tgt.write_text("\n".join(tgt))
        path_src.write_text("\n".join(src))
        num_affected += 1
        print(f"  new: {len(src)} -> {len(tgt)}")

    return num_affected


def _realign_corpus_sentences_2(out_dir, corpus):
    """Fix sentence alignment in case of two annotators changing
    the number of sentences in source.
    """

    # In some cases, the number of sentences differs between source and target.
    # This happens when:
    # - the doc has two annotators
    # - one of the annotator edits newline characters (i.e., changes the number
    #   of sentences)
    # In this case, align_sentences() correctly aligns (src, tgt1) and (src, tgt2),
    # effectively producing two versions of src of different length. We assume
    # the the source is the same for both tgt1 and tgt2, so we write only one.
    #
    # This function finds such cases and fixes them by joining some sentences
    # in whatever file out of (src, tgt1, tgt2) has more sentences.
    num_affected = 0
    for doc in tqdm.tqdm(corpus.get_documents()):

        # The problem only occurs when there are two annotators
        if doc.meta.annotator_id != 2:
            continue

        path_src = out_dir / "source-sentences" / f"{doc.doc_id}.src.txt"
        path_tgt1 = out_dir / "target-sentences" / f"{doc.doc_id}.a1.txt"
        path_tgt2 = out_dir / "target-sentences" / f"{doc.doc_id}.a2.txt"

        src = path_src.read_text().split("\n")
        tgt1 = path_tgt1.read_text().split("\n")
        tgt2 = path_tgt2.read_text().split("\n")

        if len(src) == len(tgt1) == len(tgt2):
            continue  # no problem here
        
        num_affected += 1
        print(f"Fixing sentence alignment for {doc.doc_id}")
        print(f"  src: {len(src)} sentences")
        print(f" tgt1: {len(tgt1)} sentences")
        print(f" tgt2: {len(tgt2)} sentences")

        # Make sure the source has joined sentences
        if len(src) > len(tgt1):
            src, tgt1 = align_sentences(src, tgt1)
        if len(src) > len(tgt2):
            src, tgt2 = align_sentences(src, tgt2)

        # Make sure that both tagets match the source
        if len(tgt1) > len(src):
            src, tgt1 = align_sentences(src, tgt1)
        if len(tgt2) > len(src):
            src, tgt2 = align_sentences(src, tgt2)

        if not (len(src) == len(tgt1) == len(tgt2)):
            print("  FAILED TO FIX ALIGNMENT")
            print(f"  src: {len(src)} sentences")
            print(f" tgt1: {len(tgt1)} sentences")
            print(f" tgt2: {len(tgt2)} sentences")

        # Write the fixed files
        path_src.write_text("\n".join(src) + "\n")
        path_tgt1.write_text("\n".join(tgt1) + "\n")
        path_tgt2.write_text("\n".join(tgt2) + "\n")

    return num_affected


def _tokenize_corpus(out_dir, corpus):
    """Write tokenized sentences. """

    for doc in tqdm.tqdm(corpus.get_documents()):
        fname_src = f"{doc.doc_id}.src.txt"
        fname_tgt = f"{doc.doc_id}.a{doc.meta.annotator_id}.txt"
        path_src = out_dir / "source-sentences-tokenized" / fname_src
        path_tgt = out_dir / "target-sentences-tokenized" / fname_tgt
        src_sents = (out_dir / "source-sentences" / fname_src).read_text().split("\n")
        tgt_sents = (out_dir / "target-sentences" / fname_tgt).read_text().split("\n")
        path_src.parent.mkdir(exist_ok=True)
        path_tgt.parent.mkdir(exist_ok=True)
        tokenized_src = [tokenize(s) for s in src_sents]
        tokenized_tgt = [tokenize(s) for s in tgt_sents]
        path_src.write_text("\n".join(tokenized_src))
        path_tgt.write_text("\n".join(tokenized_tgt))


def align_sentences(src_sentences, tgt_sentences):
    combinations = [
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 1),
        (3, 1),
        (2, 2),
    ]
    result_src = []
    result_tgt = []
    pos_src = 0
    pos_tgt = 0
    while pos_src < len(src_sentences):
        min_dist = 10e9
        best_take_src = None
        best_take_tgt = None
        best_src = None
        best_tgt = None
        for take_src, take_tgt in combinations:

            # If take_src reaches the end of source, make sure that we
            # reach the end of target as well
            if pos_src + take_src >= len(src_sentences):
                take_tgt = len(tgt_sentences) - pos_tgt

            src = " ".join(src_sentences[pos_src : pos_src + take_src])
            tgt = " ".join(tgt_sentences[pos_tgt : pos_tgt + take_tgt])
            dist = damerau_levenshtein_distance(src, tgt)
            if dist < min_dist:
                min_dist = dist
                best_take_src = take_src
                best_take_tgt = take_tgt
                best_src = src
                best_tgt = tgt
        pos_src += best_take_src
        pos_tgt += best_take_tgt
        result_src.append(best_src)
        result_tgt.append(best_tgt)
    assert len(result_src) == len(result_tgt)
    return result_src, result_tgt


def split_sentences(text: str) -> [str]:
    sentences = []
    if not hasattr(split_sentences, "nlp"):
        stanza.download("uk")
        split_sentences.nlp = stanza.Pipeline(lang="uk", processors="tokenize")
    nlp = split_sentences.nlp

    for paragraph in text.split("\n"):
        sentences += [s.text for s in nlp(paragraph).sentences]

    return sentences


def tokenize(text: str) -> [str]:
    if not hasattr(tokenize, "nlp"):
        tokenize.nlp = stanza.Pipeline(lang="uk", processors="tokenize")
    nlp = tokenize.nlp

    tokenized = " ".join([t.text for t in nlp(text).iter_tokens()])
    return tokenized


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="./data")
    parser.add_argument("--annotation-layer",
                        choices=[x.value for x in ua_gec.AnnotationLayer],
                        required=True)
    args = parser.parse_args()
    main(args.path, args.annotation_layer)
