#!/usr/bin/env python3
"""Evaluate the model output with Errant.

Usage:
    evaluate.py <corrected> [--no-tokenize] --layer <layer>
    evaluate.py (-h | --help)

Options:
    -h --help           Show this screen.
    --no-tokenize       Do not tokenize the input.
    --layer <layer>     Annotation layer to evaluate: `gec-only` or `gec-fluency`.

<corrected> is the path to the model output. If --no-tokenize is not specified,
the input will be tokenized before evaluation.

"""

import argparse
import subprocess
import sys
from pathlib import Path

import stanza
import ua_gec


def tokenize(text: str) -> [str]:
    if not hasattr(tokenize, "nlp"):
        tokenize.nlp = stanza.Pipeline(lang="uk", processors="tokenize")
    nlp = tokenize.nlp

    tokenized = " ".join([t.text for t in nlp(text).iter_tokens()])
    return tokenized


def tokenize_file(input_file: Path, output_file: Path):
    with open(input_file) as f, open(output_file, "w") as out:
        for line in f:
            line = line.rstrip("\n")
            tokenized = tokenize(line)
            out.write(tokenized + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("corrected", type=str, help="Path to the model output")
    parser.add_argument("--no-tokenize", action="store_true", help="Do not tokenize the input")
    parser.add_argument("--layer", type=ua_gec.AnnotationLayer, required=True,
            help="Annotation layer to evaluate: `gec-only` or `gec-fluency`")
    args = parser.parse_args()


    # Path to m2 file
    data_dir = Path(__file__).parent / ".." / "data"
    if args.layer == ua_gec.AnnotationLayer.GecOnly:
        m2_path = data_dir / "gec-only/test/gec-only.test.m2"
    elif args.layer == ua_gec.AnnotationLayer.GecAndFluency:
        m2_path = data_dir / "gec-fluency/test/gec-fluency.test.m2"
    else:
        raise ValueError(f"Unknown layer: {args.layer}")

    # Tokenize input
    if args.no_tokenize:
        tokenized_path = args.corrected
    else:
        tokenized_path = f"{args.corrected}.tok"
        tokenize_file(args.corrected, tokenized_path)
    print(f"Tokenized input: {tokenized_path}", file=sys.stderr)

    # Get the source text out of m2
    source_path = f"{args.corrected}.src"
    with open(m2_path) as f, open(source_path, "w") as out:
        for line in f:
            if line.startswith("S "):
                out.write(line[2:])

    # Align tokenized input with the original text with Errant
    m2_input = f"{tokenized_path}.m2"
    subprocess.run(["errant_parallel", "-orig", source_path, "-cor", tokenized_path, "-out", m2_input], check=True)
    print(f"Aligned input: {m2_input}", file=sys.stderr)

    # Evaluate
    subprocess.run(["errant_compare", "-hyp", m2_input, "-ref", m2_path])


if __name__ == "__main__":
    main()
