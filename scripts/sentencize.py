#!/usr/bin/env python3
from pathlib import Path
import stanza
import tqdm
import ua_gec
from grampy.text import edit_distance


def main(data_dir="./data"):
    data_dir = Path(data_dir)
    for partition in ("train", "test"):
        do_partition(data_dir / partition, ua_gec.Corpus(partition))


def do_partition(out_dir, corpus):
    for doc in tqdm.tqdm(corpus.get_documents()):
        src = split_sentences(doc.source)
        tgt = split_sentences(doc.target)
        fname_src = f"{doc.doc_id}.src.txt"
        fname_tgt = f"{doc.doc_id}.a{doc.meta.annotator_id}.txt"
        path_src = out_dir / "source-sentences" / fname_src
        path_tgt = out_dir / "target-sentences" / fname_tgt
        output_src, output_tgt = align_sentences(src, tgt)
        path_src.parent.mkdir(exist_ok=True)
        path_tgt.parent.mkdir(exist_ok=True)
        path_src.write_text("\n".join(output_src))
        path_tgt.write_text("\n".join(output_tgt))


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
            dist = edit_distance(src, tgt)
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
    if not hasattr(split_sentences, "nlp"):
        split_sentences.nlp = stanza.Pipeline(lang="uk", processors="tokenize")
    nlp = split_sentences.nlp

    sentences = [s.text for s in nlp(text).sentences]
    return sentences


if __name__ == "__main__":
    main()
