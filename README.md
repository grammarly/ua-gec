[Українською](./README_ua.md)

# UA-GEC: Grammatical Error Correction and Fluency Corpus for the Ukrainian Language

This repository contains UA-GEC data and an accompanying Python library.

## What's new

* **May 2023**: [Shared Task on Ukrainian GEC](https://unlp.org.ua/shared-task/) results published.
* **November 2022**: Version 2.0 released, featuring more data and detailed annotations.
* **January 2021**: Initial release.

See [CHANGELOG.md](./CHANGELOG.md) for detailed updates.


## Data

All corpus data and metadata stay under the `./data`. It has two subfolders
for [gec-fluency and gec-only corpus versions](#annotation-format)

Both corpus versions contain two subfolders [train and test splits](#train-test-split) with different data
representations:

`./data/{gec-fluency,gec-only}/{train,test}/annotated` stores documents in the [annotated format](#annotation-format)

`./data/{gec-fluency,gec-only}/{train,test}/source` and `./data/{gec-fluency,gec-only}/{train,test}/target` store the
original and the corrected versions of documents. Text files in these
directories are plain text with no annotation markup. These files were
produced from the annotated data and are, in some way, redundant. We keep them
because this format is convenient in some use cases.

`./data/{gec-fluency,gec-only}/test/*.m2` contains M2 files.


## Metadata

`./data/metadata.csv` stores per-document metadata. It's a CSV file with
the following fields:

- `id` (str): document identifier;
- `author_id` (str): document author identifier;
- `is_native` (int): 1 if the author is native-speaker, 0 otherwise;
- `region` (str): the author's region of birth. A special value "Інше"
  is used both for authors who were born outside Ukraine and authors
  who preferred not to specify their region.
- `gender` (str): could be "Жіноча" (female), "Чоловіча" (male), or "Інша" (other);
- `occupation` (str): one of "Технічна", "Гуманітарна", "Природнича", "Інша";
- `submission_type` (str): one of "essay", "translation", or "text\_donation";
- `source_language` (str): for submissions of the "translation" type, this field
    indicates the source language of the translated text. Possible values are
    "de", "en", "fr", "ru", and "pl";
- `annotator_id` (int): ID of the annotator who corrected the document;
- `partition` (str): one of "test" or "train";
- `is_sensitive` (int): 1 if the document contains profanity or offensive language.

## Annotation format

Annotated files are text files that use the following in-text annotation format:
`{error=>edit:::error_type=Tag}`, where `error` and `edit` stand for a text item before
and after correction respectively, and `Tag` denotes an error category and an error subcategory in case of Grammar- and Fluency-related errors.

Example of an annotated sentence:
```
    I {likes=>like:::error_type=G/Number} turtles.
```

Below you can see a list of error types presented in the corpus:
- `Spelling`: spelling errors;
- `Punctuation`: punctuation errors.

Grammar-related errors:
- `G/Case`: incorrect usage of case of any notional part of speech;
- `G/Gender`: incorrect usage of gender of any notional part of speech;
- `G/Number`: incorrect usage of number of any notional part of speech;
- `G/Aspect`: incorrect usage of verb aspect;
- `G/Tense`: incorrect usage of verb tense;
- `G/VerbVoice`: incorrect usage of verb voice;
- `G/PartVoice`:  incorrect usage of participle voice;
- `G/VerbAForm`:  incorrect usage of an analytical verb form;
- `G/Prep`: incorrect preposition usage;
- `G/Participle`: incorrect usage of participles;
- `G/UngrammaticalStructure`: digression from syntactic norms;
- `G/Comparison`: incorrect formation of comparison degrees of adjectives and adverbs;
- `G/Conjunction`: incorrect usage of conjunctions;
- `G/Other`: other grammatical errors.

Fluency-related errors:
- `F/Style`: style errors;
- `F/Calque`: word-for-word translation from other languages;
- `F/Collocation`: unnatural collocations;
- `F/PoorFlow`: unnatural sentence flow;
- `F/Repetition`: repetition of words;
- `F/Other`: other fluency errors.


An accompanying Python package, `ua_gec`, provides many tools for working with
annotated texts. See its documentation for details.


## Train-test split

We expect users of the corpus to train and tune their models on the __train__ split
only. Feel free to further split it into train-dev (or use cross-validation).

Please use the __test__ split only for reporting scores of your final model.
In particular, never optimize on the test set. Do not tune hyperparameters on
it. Do not use it for model selection in any way.

Next section lists the per-split statistics.


## Statistics

UA-GEC contains:

### GEC+Fluency

| Split     | Documents | Sentences |  Tokens | Authors | Errors | 
|:---------:|:---------:|----------:|--------:|:-------:|--------|
| train     | 1,706     | 31,038    | 457,017 | 752     | 38,213 |
| test      |   166     |  2,697    | 43,601  | 76      |  7,858 |
| **TOTAL** | 1,872     | 33,735    | 500,618 | 828     | 46,071 |

See [stats.gec-fluency.txt](./stats.gec-fluency.txt) for detailed statistics.


### GEC-only

| Split     | Documents | Sentences |  Tokens | Authors | Errors | 
|:---------:|:---------:|----------:|--------:|:-------:|--------|
| train     | 1,706     | 31,046    | 457,004 | 752     | 30,049 |
| test      |   166     |  2,704    |  43,605 |  76     |  6,169 |
| **TOTAL** | 1,872     | 33,750    | 500,609 | 828     | 36,218 |

See [stats.gec-only.txt](./stats.gec-only.txt) for detailed statistics.


## Python library

Alternatively to operating on data files directly, you may use a Python package
called `ua_gec`. This package includes the data and has classes to iterate over
documents, read metadata, work with annotations, etc.

### Getting started

The package can be easily installed by `pip`:

```
    $ pip install ua_gec
```

Alternatively, you can install it from the source code:

```
    $ cd python
    $ python setup.py develop
```


### Iterating through corpus

Once installed, you may get annotated documents from the Python code:

```python
    
    >>> from ua_gec import Corpus
    >>> corpus = Corpus(partition="train", annotation_layer="gec-only")
    >>> for doc in corpus:
    ...     print(doc.source)         # "I likes it."
    ...     print(doc.target)         # "I like it."
    ...     print(doc.annotated)      # <AnnotatedText("I {likes=>like} it.")
    ...     print(doc.meta.region)    # "Київська"
```

Note that the `doc.annotated` property is of type `AnnotatedText`. This
class is described in the [next section](#working-with-annotations)


### Working with annotations

`ua_gec.AnnotatedText` is a class that provides tools for processing
annotated texts. It can iterate over annotations, get annotation error
type, remove some of the annotations, and more.

Here is an example to get you started. It will remove all F/Style annotations from a text:

```python
    >>> from ua_gec import AnnotatedText
    >>> text = AnnotatedText("I {likes=>like:::error_type=G/Number} it.")
    >>> for ann in text.iter_annotations():
    ...     print(ann.source_text)       # likes
    ...     print(ann.top_suggestion)    # like
    ...     print(ann.meta)              # {'error_type': 'Grammar'}
    ...     if ann.meta["error_type"] == "F/Style":
    ...         text.remove(ann)         # or `text.apply_correction(ann)`
```


## Multiple annotators

Some documents are annotated with multiple annotators. Such documents
share `doc_id` but differ in `doc.meta.annotator_id`.

Currently, test sets for gec-fluency and gec-only are annotated by two annotators.
The train sets contain 45 double-annotated docs.


## Contributing

* Data and code improvements are welcomed. Please submit a pull request.


## Citation

The [accompanying paper](https://arxiv.org/abs/2103.16997) is:

```
@inproceedings{syvokon-etal-2023-ua,
    title = "{UA}-{GEC}: Grammatical Error Correction and Fluency Corpus for the {U}krainian Language",
    author = "Syvokon, Oleksiy  and
      Nahorna, Olena  and
      Kuchmiichuk, Pavlo  and
      Osidach, Nastasiia",
    booktitle = "Proceedings of the Second Ukrainian Natural Language Processing Workshop (UNLP)",
    month = may,
    year = "2023",
    address = "Dubrovnik, Croatia",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.unlp-1.12",
    pages = "96--102",
    abstract = "We present a corpus professionally annotated for grammatical error correction (GEC) and fluency edits in the Ukrainian language. We have built two versions of the corpus {--} GEC+Fluency and GEC-only {--} to differentiate the corpus application. To the best of our knowledge, this is the first GEC corpus for the Ukrainian language. We collected texts with errors (33,735 sentences) from a diverse pool of contributors, including both native and non-native speakers. The data cover a wide variety of writing domains, from text chats and essays to formal writing. Professional proofreaders corrected and annotated the corpus for errors relating to fluency, grammar, punctuation, and spelling. This corpus can be used for developing and evaluating GEC systems in Ukrainian. More generally, it can be used for researching multilingual and low-resource NLP, morphologically rich languages, document-level GEC, and fluency correction. The corpus is publicly available at https://github.com/grammarly/ua-gec",
}
```


## Contacts

* nastasiya.osidach@grammarly.com
* olena.nahorna@grammarly.com
* oleksiy.syvokon@gmail.com
* pavlo.kuchmiichuk@gmail.com
