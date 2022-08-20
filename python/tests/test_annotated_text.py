import pytest
from ua_gec.annotated_text import (
    AnnotatedText,
    MutableText,
    Annotation,
    OverlapError,
)


class TestMutableText:
    def test_edits_in_arbitrary_order(self):
        # Order in which edits are made should not matter
        text = MutableText("one two three")
        text.replace(4, 7, "TWO")
        text.replace(0, 3, "ONE")
        assert text.get_edited_text() == "ONE TWO three"

    def test_apply_edits_changes_offsets(self):
        # Given mutable text with edits
        text = MutableText("one two three")
        text.replace(0, 3, "1")

        # When edits applied
        text.apply_edits()

        # Then the source text should be replaced with the edited version
        assert text.get_source_text() == "1 two three"

        # Then positions of the new string should come in effect
        text.replace(2, 5, "2")
        assert text.get_edited_text() == "1 2 three"

    def test_get_source_text(self):
        # Given mutable text with edits
        text = MutableText("one two three")
        text.replace(0, 3, "1")

        # When reading `source` property, the unedited text should be returned
        assert text.get_source_text() == "one two three"


class TestAnnotationOverlap:
    def test_default(self):
        text = AnnotatedText("{helllo=>Hello} {world=>World}")
        with pytest.raises(OverlapError):
            text.annotate(2, 5, "ll")

    def test_error(self):
        text = AnnotatedText("{helllo=>Hello} {world=>World}")
        with pytest.raises(OverlapError):
            text.annotate(2, 5, "ll")


def test_get_annotations():
    text = AnnotatedText(
        "this {was=>is|will be} an {anotated=>annotated} text"
    )
    anns = text.get_annotations()
    assert len(anns) == 2
    assert anns[0].source_text == "was"
    assert anns[0].suggestions == ["is", "will be"]
    assert anns[0].start == len("this ")
    assert anns[0].end == len("this was")

    assert anns[1].source_text == "anotated"
    assert anns[1].suggestions == ["annotated"]
    assert anns[1].start == len("this was an ")
    assert anns[1].end == len("this was an anotated")


def test_get_annoation_at():
    text = AnnotatedText("Hello {word=>world}")
    print(text.get_annotations())
    assert text.get_annotation_at(0) is None
    assert text.get_annotation_at(0, 100) is None
    assert text.get_annotation_at(6, 10).source_text == "word"
    assert text.get_annotation_at(6).source_text == "word"
    assert text.get_annotation_at(7).source_text == "word"
    assert text.get_annotation_at(10) is None
    assert text.get_annotation_at(11) is None


def test_get_original_text():
    text = AnnotatedText("{helo=>Hello} world!")
    expected = "helo world!"
    assert text.get_original_text() == expected


def test_get_corrected_text():
    text = AnnotatedText("{helo=>Hello} world!")
    expected = "Hello world!"
    assert text.get_corrected_text() == expected


def test_get_original_text_with_highlight():
    text = AnnotatedText("{helo=>NO_SUGGESTIONS} world!")
    expected = "helo world!"
    assert text.get_original_text() == expected


def test_get_corrected_text_with_highlight():
    text = AnnotatedText("{helo=>NO_SUGGESTIONS} world!")
    expected = "helo world!"
    assert text.get_corrected_text() == expected


def test_get_annotated_text_with_highlight():
    text = AnnotatedText("{helo=>NO_SUGGESTIONS} world!")
    expected = "{helo=>NO_SUGGESTIONS} world!"
    assert text.get_annotated_text() == expected


def test_get_corrected_text_on_the_level():
    text = AnnotatedText("{helo=>Hello|hola} {word=>world}!")
    expected = "hola word!"
    assert text.get_corrected_text(level=1) == expected


def test_get_annotated_text_same_span():
    text = AnnotatedText("{=>b}{=>a}")
    assert text.get_annotated_text() == "{=>b}{=>a}"


def test_remove():
    # Given annotated text
    text = AnnotatedText("{helo=>Hello} {word=>World}!")

    # When removing single annotation
    annotation = text.get_annotations()[1]
    assert annotation.source_text == "word"
    text.remove(annotation)

    # Then all other annotations should stay
    expected = "{helo=>Hello} word!"
    assert text.get_annotated_text() == expected
    assert len(text.get_annotations()) == 1


def test_remove_non_existing_annotation():
    # Given annotated text
    text = AnnotatedText("{helo=>Hello} {word=>World}!")

    # When removing annotation that doesn't exists in the text
    # Then error should be raised
    annotation = text.get_annotations()[0]
    text.remove(annotation)
    with pytest.raises(ValueError):
        text.remove(annotation)


def test_apply_correction():
    # Given annotated text
    text = AnnotatedText("{helo=>Hello}{...=>,} {word=>World}!")

    # When applying the corrected text of an annotation
    ann = text.get_annotations()[1]  # {...=>,}
    text.apply_correction(ann)

    # Then annotation should be removed, and the correct text used instead
    assert text.get_annotated_text() == "{helo=>Hello}, {word=>World}!"


def test_apply_correction_with_no_suggestions():
    # Given annotated text
    text = AnnotatedText("Hi {sdf=>NO_SUGGESTIONS}!")

    # When applyinng a no-suggestions annotation
    ann = text.get_annotations()[0]
    text.apply_correction(ann)

    # Then the annotation should be replaced with the original text
    assert text.get_annotated_text() == "Hi sdf!"


def test_iter_annotations():
    # Given annotated text
    text = AnnotatedText("{helo=>Hello}{...=>,} {word=>World}!")

    #  When changing annotations during annotations iteration
    for i, ann in enumerate(text.iter_annotations()):
        if i == 1:
            text.remove(ann)  # {...=>,}
        else:
            text.apply_correction(ann)

    # Then the text should be correctly updated
    assert text.get_annotated_text() == "Hello... World!"


def test_apply_correction_insert_word():
    text = AnnotatedText("{=>Hello} {word=>World}!")

    ann = text.get_annotations()[0]  # {=>Hello}
    text.apply_correction(ann)

    assert text.get_annotated_text() == "Hello {word=>World}!"


def test_curly_braces_in_original_text():
    text = AnnotatedText(r"(e.g. \emph{the, {dox=>fox}, jumps})")
    expected = r"(e.g. \emph{the, dox, jumps})"
    assert text.get_original_text() == expected

def test_newline_in_annotation():
    text = AnnotatedText(r"One{; =>\n}Two")
    assert text.get_original_text() == "One; Two"
    assert text.get_corrected_text() == "One\nTwo"
    assert text.get_annotations()[0].suggestions == ["\n"]
    assert text.get_annotated_text() == r"One{; =>\n}Two"

def test_newline_in_annotation_in_source():
    text = AnnotatedText(r"One {1\n2=>1. 2.}Two")
    assert text.get_original_text() == "One 1\n2Two"
    assert text.get_corrected_text() == "One 1. 2.Two"
    assert text.get_annotations()[0].suggestions == ["1. 2."]
    assert text.get_annotated_text() == r"One {1\n2=>1. 2.}Two"

def test_string_representation():
    # AnnotatedText should pretend
    text = AnnotatedText("Hello {word=>world}!")
    expected = "Hello {word=>world}!"
    assert str(text) == expected


def test_repr():
    text = AnnotatedText("Hello {word=>world}!")
    expected = "<AnnotatedText('Hello {word=>world}!')>"
    assert repr(text) == expected


def test_not_eq_other_type():
    text = "Text {=>tokens} tokens ."
    text_1 = AnnotatedText(text)
    assert text_1 != text


def test_eq():
    text = "Text {=>tokens} tokens ."
    text_1 = AnnotatedText(text)
    text_2 = AnnotatedText(text)
    assert text_1 == text_2


def test_eq_2():
    t1 = AnnotatedText("hello word")
    t2 = AnnotatedText("hello word")
    t1.annotate(0, 5, "Hello")
    t1.annotate(6, 10, "world")
    t2.annotate(6, 10, "world")
    t2.annotate(0, 5, "Hello")
    assert t1 == t2


def test_wrong_constructor_params():

    # Constructing AnnotatedText from anything other than string is forbidden

    with pytest.raises(ValueError):
        AnnotatedText(42)

    annotated = AnnotatedText("hello")
    with pytest.raises(ValueError):
        AnnotatedText(annotated)


def test_not_eq():
    text_1 = AnnotatedText("Text {=>tokens} tokens .")
    text_2 = AnnotatedText("Text {=>TOKENS} tokens .")
    assert text_1 != text_2


class Test_annotate:
    def test_forbid_joining_annotation_with_multiple_suggestions(self):
        text = AnnotatedText("helloworld")
        text.annotate(0, len("helloworld"), ["hello", "hola", "hi"])
        with pytest.raises(OverlapError):
            text.annotate(0, len("helloworld"), "world")

    def test_annotate_empty_lengthy_intersect(self):
        text = AnnotatedText("Did n't know it.")
        text.annotate(12, 12, [" about"])
        with pytest.raises(OverlapError):
            text.annotate(0, len("Did n't know it."), ["Did n't know it"])

    def test_annotate_with_none(self):
        # Some checks return None in place of suggestions, meaning
        # that there are no good suggestions.
        # The convention for those in the light-annotated format is
        # {bad=>NO_SUGGESTIONS} annotation.
        text = AnnotatedText("asdasd")
        text.annotate(0, len("asdasd"), correct_value=None)
        assert text.get_annotated_text() == "{asdasd=>NO_SUGGESTIONS}"

        # When parsed, special value of "NO_SUGGESTIONS" should be
        # represented as empty suggestions list
        assert text.get_annotations()[0].suggestions == []

    def test_parse_no_suggestions(self):
        # When parsing text with the special "NO_SUGGESTIONS" value
        text = AnnotatedText("{asdasd=>NO_SUGGESTIONS}")

        # Then empty suggestions list should be returned
        ann = text.get_annotations()[0]
        assert ann.suggestions == []

    def test_join_by(self):
        t1 = AnnotatedText("I {likes=>like:::error_type=SVA} turtles.")
        t2 = AnnotatedText("I{,=>:::error_type=Punct} like turtles.")

        actual = AnnotatedText.join("\n", [t1, t2])
        expected = AnnotatedText(
            "I {likes=>like:::error_type=SVA} turtles.\n"
            "I{,=>:::error_type=Punct} like turtles."
        )

        assert expected == actual


class TestAnnotation:
    def test_to_str(self):
        ann = Annotation(0, 4, "helo", ["hello", "hola"])
        expected = "{helo=>hello|hola}"
        assert ann.to_str() == expected

    def test_meta(self):
        meta = {"pname": "Spelling"}
        ann = Annotation(0, 4, "helo", ["hello", "hola"], meta=meta)
        assert ann.meta["pname"] == "Spelling"

    def test_meta_not_reused(self):
        a = Annotation(0, 4, "helo", ["hello", "hola"])
        b = Annotation(0, 4, "helo", ["hello", "hola"])
        a.meta["x"] = "y"
        assert b.meta == {}

    def test_top_suggestion(self):
        ann1 = Annotation(0, 4, "helo", ["hello", "hola"])
        assert ann1.top_suggestion == "hello"

        ann2 = Annotation(0, 4, "helo", [])
        assert ann2.top_suggestion == None

    def test_hash(self):
        ann1 = Annotation(0, 4, "helo", ["hello", "hola"])
        ann2 = Annotation(0, 4, "helo", ["hello", "hola"])
        ann3 = Annotation(0, 4, "helo", ["hello", "hola", "привіт"])

        assert hash(ann1) == hash(ann2)
        assert hash(ann1) != hash(ann3)

        my_set = {ann1, ann2, ann3}
        assert len(my_set) == 2

    def test_equality(self):
        ann1 = Annotation(0, 4, "helo", ["hello", "hola"])
        ann2 = Annotation(0, 4, "helo", ["hello", "hola"])
        ann3 = Annotation(0, 4, "helo", ["hello", "hola", "привіт"])

        assert ann1 == ann2
        assert ann1 != ann3
        assert ann1 != None
        assert ann1 != "{helo=>hello|hola}"


class TestParseMeta:
    def test_to_str(self):
        text = AnnotatedText("helo world")
        text.annotate(
            0, 4, ["hello", "hola"], meta={"key": "value with spaces"}
        )
        expected = "{helo=>hello|hola:::key=value with spaces} world"
        assert text.get_annotated_text() == expected

    def test_parse(self):
        text = AnnotatedText(
            "Hello {wold=>World|world:::type=OOV Spell:::status=ok}"
        )

        expected_original = "wold"
        expected_sugg = ["World", "world"]
        expected_meta = {"type": "OOV Spell", "status": "ok"}

        ann = text.get_annotations()[0]
        assert ann.meta == expected_meta
        assert ann.suggestions == expected_sugg
        assert ann.source_text == expected_original

    def test_parse_colon(self):
        text = AnnotatedText("text {.=>::::key=R:PUNCT}")

        expected = AnnotatedText("text .")
        expected.annotate(5, 6, ":", meta={"key": "R:PUNCT"})

        ann = text.get_annotations()[0]
        expected_ann = expected.get_annotations()[0]
        assert ann.meta == expected_ann.meta
        assert ann.suggestions == expected_ann.suggestions
        assert ann.source_text == expected_ann.source_text
