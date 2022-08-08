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
        print(f"~~~ Preprocess {partition} partition")
        corpus = ua_gec.Corpus(partition, annotation_layer=annotation_layer)
        do_partition(data_dir / partition, corpus)


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

        # Write tokenized sentences
        path_src = out_dir / "source-sentences-tokenized" / fname_src
        path_tgt = out_dir / "target-sentences-tokenized" / fname_tgt
        path_src.parent.mkdir(exist_ok=True)
        path_tgt.parent.mkdir(exist_ok=True)
        tokenized_src = [tokenize(s) for s in output_src]
        tokenized_tgt = [tokenize(s) for s in output_tgt]
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
    main(args.path)
