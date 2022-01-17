# Changelog

## [1.3.0.dev0] - 2022-01-17
### Added
- Annotations may indicate newline insertion/deletion by using the "\n" token

### Changed
- Fix annotations in ~10 docs (lists, tables, newlines)
- Sentence-split source and target files are now guaranteed to have the same
  number of lines

## [1.2.1] - 2021-05-25
### Changed
- Fixed bug with `is_sensitive` metadata

## [1.2.0] - 2021-05-25
### Added
- Sentence-level aligned data
- Tokenized doc-level and sentence-level data

## [1.1.1] - 2021-04-09
### Added
- `Corpus.get_doc()` method to find a document by id.

## [1.1.0] - 2021-02-05
### Added
- `is_sensitive` metadata flag to mark documents that contain profanity.
- `stats.txt` contains detailed dataset statistics

## [1.0.0] - 2021-01-20

### Added
- 1,011 annotated documents (20,715 sentences)
- A Python package, `ua-gec` to work with annotations
