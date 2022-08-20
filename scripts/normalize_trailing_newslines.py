#!/usr/bin/env python3
"""Modify files in-place to ensure that there is no trailing newlines."""
import os
import sys
import glob
import argparse


def normalize_trailing_newslines(path):
    """Normalize trailing newlines in a file."""
    with open(path, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.rstrip('\n') + '\n')


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help='path to file or directory', nargs='+')
    args = parser.parse_args()
    for path in args.path:
        print(path)
        normalize_trailing_newslines(path)


if __name__ == '__main__':
    main()
