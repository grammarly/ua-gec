from collections import namedtuple
import re


class OverlapError(Exception):
    pass


NO_SUGGESTIONS = "NO_SUGGESTIONS"

DEFAULT = object()


class MutableText:
    """Represents text that can be modified."""

    def __init__(self, text):
        self._text = text
        self._edits = []

    def __str__(self):
        """Pretend to be a normal string. """
        return self.get_edited_text()

    def __repr__(self):
        return "<MutableText({})>".format(repr(str(self)))

    def replace(self, start, end, value):
        """Replace substring with a value.

        Example:
            >>> t = MutableText('the red fox')
            >>> t.replace(4, 7, 'brown')
            >>> t.get_edited_text()
            'the brown fox'

        """
        self._edits.append((start, end, value))  # TODO: keep _edits sorted?

    def apply_edits(self):
        """Applies all edits made so far.  """

        self._text = self.get_edited_text()
        self._edits = []

    def get_source_text(self):
        """Return string without pending edits applied.

        Example:
            >>> t = MutableText('the red fox')
            >>> t.replace(4, 7, 'brown')
            >>> t.get_source_text()
            'the red fox'
        """
        return self._text

    def get_edited_text(self):
        """Return text with all corrections applied. """

        result = []
        i = 0
        t = self._text
        for begin, end, val in sorted(self._edits, key=lambda x: (x[0], x[1])):
            result.append(t[i:begin])
            result.append(val)
            i = end
        result.append(t[i:])
        return "".join(result)


class AnnotatedText:
    """Text representation that allows easy replacements and annotations.

    This class also supports parsing meta data from annotations.

    Example:
        >>> s = 'Hi {wold=>World|world:::type=OOV Spell:::status=ok}'
        >>> anns = AnnotatedText(s).get_annotations()
        >>> anns[0].suggestions
        ['World', 'world']
        >>> anns[0].meta
        {'type': 'OOV Spell', 'status': 'ok'}

    """

    ANNOTATION_PATTERN = re.compile(r"\{([^{]*)=>(.*?)(:::[^:][^}]*)?\}")

    def __init__(self, text: str) -> None:

        if not isinstance(text, str):
            raise ValueError(f"`text` must be string, not {type(text)}")

        unescape_source = lambda m: _unescape(m.groups()[0])
        original = self.ANNOTATION_PATTERN.sub(unescape_source, text)
        self._annotations = self._parse(text)
        self._text = original

    def __str__(self):
        """Pretend to be a normal string. """
        return self.get_annotated_text()

    def __repr__(self):
        return "<AnnotatedText('{}')>".format(self.get_annotated_text())

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        if self._text != other._text:
            return False

        if len(self._annotations) != len(other._annotations):
            return False

        for ann in other._annotations:
            if ann != self.get_annotation_at(ann.start, ann.end):
                return False

        return True

    def annotate(
        self,
        start,
        end,
        correct_value,
        append=None,
        meta=None,
    ):

        """Annotate substring as being corrected.

        Args:
            start (int): starting position of the substring to annotate.
            end (int): ending position of the substring to annotate.
            correct_value (str, iterable, None):
                one or more correction suggestions.
            meta (dict, optional): any additional info associated with the
                annotation. Defaults to an empty dict.

        Example:
            >>> t = AnnotatedText('the red fox')
            >>> t.annotate(4, 7, ['brown', 'white'])
            >>> t.get_annotated_text()
            'the {red=>brown|white} fox'

        """
        if start > end:
            raise ValueError(
                f"Start positition {start} should not greater "
                f"than end position {end}"
            )

        if meta is None:
            meta = dict()

        bad = self._text[start:end]

        if isinstance(correct_value, str):
            suggestions = [correct_value]
        elif correct_value is None:
            suggestions = []
        else:
            suggestions = list(correct_value)

        new_ann = Annotation(start, end, bad, suggestions, meta)
        overlapping = self._get_overlaps(start, end)
        if overlapping:
            raise OverlapError(
                f"Overlap detected: positions ({start}, {end}) with "
                f"{len(overlapping)} existing annotations."
            )
        self._annotations.append(new_ann)

    def _get_overlaps(self, start, end):
        """Find all annotations that overlap with given range. """

        res = []
        for ann in self._annotations:
            if span_intersect([(ann.start, ann.end)], start, end) != -1:
                res.append(ann)
            elif start == end and ann.start == ann.end and start == ann.start:
                res.append(ann)

        return res

    def undo_edit_at(self, index):
        """Undo the last edit made at the given position. """
        for i, (start, end, val) in enumerate(reversed(self._edits)):
            if start == index:
                self._edits.pop(-i - 1)
                return
        raise IndexError()

    def get_annotations(self):
        """Return list of all annotations in the text. """

        return self._annotations

    def iter_annotations(self):
        """Iterate the annotations in the text.

        This differs from `get_annotations` in that you can safely modify
        current annotation during the iteration. Specifically, `remove` and
        `apply_correction` are allowed. Adding and modifying annotations other
        than the one being iterated is not yet well-defined!

        Example:
            >>> text = AnnotatedText('{1=>One} {2=>Two} {3=>Three}')
            >>> for i, ann in enumerate(text.iter_annotations()):
            ...     if i == 0:
            ...         text.apply_correction(ann)
            ...     else:
            ...         text.remove(ann)
            >>> text.get_annotated_text()
            'One 2 3'

        Yields:
            Annotation instances

        """

        n_anns = len(self._annotations)
        i = 0
        while i < n_anns:
            yield self._annotations[i]
            delta = len(self._annotations) - n_anns
            i += delta + 1
            n_anns = len(self._annotations)

    def get_annotation_at(self, start, end=None):
        """Return annotation at the given position or region.

        If only `start` is provided, return annotation that covers that
        source position.

        If both `start` and `end` are provided, return annotation
        that matches (start, end) span exactly.

        Return `None` if no annotation was found.
        """

        if end is None:
            for ann in self._annotations:
                if ann.start <= start < ann.end:
                    return ann
        else:
            for ann in self._annotations:
                if ann.start == start and ann.end == end:
                    return ann

        return None

    def _parse(self, text):
        """Return list of annotations found in the text. """

        anns = []
        amend = 0
        for match in self.ANNOTATION_PATTERN.finditer(text):
            source, suggestions, meta_text = match.groups()
            start = match.start() - amend
            end = start + len(_unescape(source))
            if suggestions != NO_SUGGESTIONS:
                suggestions = suggestions.split("|")
            else:
                suggestions = []

            if meta_text:
                key_values = [
                    x.partition("=") for x in meta_text.split(":::")[1:]
                ]
                meta = {k: v for k, _, v in key_values}
            else:
                meta = {}

            source = _unescape(source)
            suggestions = [_unescape(s) for s in suggestions]

            ann = Annotation(
                start=start,
                end=end,
                source_text=source,
                suggestions=suggestions,
                meta=meta,
            )
            anns.append(ann)
            amend += match.end() - match.start() - len(source)

        return anns

    def remove(self, annotation):
        """Remove annotation, replacing it with the original text. """

        try:
            self._annotations.remove(annotation)
        except ValueError:
            raise ValueError("{} is not in the list".format(annotation))

    def apply_correction(self, annotation, level=0):
        """Remove annotation, replacing it with the corrected text.

        Example:
            >>> text = AnnotatedText('{one=>ONE} {too=>two}')
            >>> a = text.get_annotations()[0]
            >>> text.apply_correction(a)
            >>> text.get_annotated_text()
            'ONE {too=>two}'
        """

        try:
            self._annotations.remove(annotation)
        except ValueError:
            raise ValueError("{} is not in the list".format(annotation))

        text = MutableText(self._text)
        if annotation.suggestions:
            repl = annotation.suggestions[level]
        else:
            repl = annotation.source_text  # for NO_SUGGESTIONS annotations
        text.replace(annotation.start, annotation.end, repl)
        self._text = text.get_edited_text()

        # Adjust other annotations
        delta = len(repl) - len(annotation.source_text)
        for i, a in enumerate(self._annotations):
            if a.start >= annotation.start:
                a = a._replace(start=a.start + delta, end=a.end + delta)
                self._annotations[i] = a

    def get_original_text(self):
        """Return the original (unannotated) text.

        Example:
            >>> text = AnnotatedText('{helo=>Hello} world!')
            >>> text.get_original_text()
            'helo world!'
        """

        return _unescape(self._text)

    def get_corrected_text(self, level=0):
        """Return the unannotated text with all corrections applied.

        Example:
            >>> text = AnnotatedText('{helo=>Hello} world!')
            >>> text.get_corrected_text()
            'Hello world!'
        """

        text = MutableText(self._text)
        for ann in self._annotations:
            try:
                text.replace(ann.start, ann.end, ann.suggestions[level])
            except IndexError:
                pass

        return _unescape(text.get_edited_text())

    def get_annotated_text(self, *, with_meta=True):
        """Return the annotated text.

        Example:
            >>> text = AnnotatedText('helo world!')
            >>> text.annotate(0, 4, 'Hello', meta={'key': 'value'})
            >>> text.get_annotated_text()
            '{helo=>Hello:::key=value} world!'
            >>> text.get_annotated_text(with_meta=False)
            '{helo=>Hello} world!'

        Args:
            with_meta: Whether to serialize `meta` fields.

        Returns:
            str
        """

        text = MutableText(self._text)
        for ann in self._annotations:
            text.replace(ann.start, ann.end, ann.to_str(with_meta=with_meta))

        return text.get_edited_text()

    @staticmethod
    def join(join_token, ann_texts):
        """Joins annotated texts by join_token.

        It's an analogy for `join_token.join(ann_texts)` but for AnnotatedText
        class.

        Args:
            join_token (str): Token to use for joining.
            ann_texts (list[AnnotatedText]): AnnotatedTexts to join.

        Returns:
            AnnotatedText
        """

        for ann_text in ann_texts:
            if not isinstance(ann_text, AnnotatedText):
                raise ValueError(
                    f"{str(ann_text)} is not of class AnnotatedText"
                )

        s = join_token.join(str(a) for a in ann_texts)

        return AnnotatedText(s)
    
def _escape(s):
    return s.replace("\n", "\\n")

def _unescape(s):
    return s.replace("\\n", "\n")


class Annotation(
    namedtuple(
        "Annotation", ["start", "end", "source_text", "suggestions", "meta"]
    )
):
    """A single annotation in the text.

    Args:
        start: starting position in the original text.
        end: ending position in the original text.
        source_text: piece of the original text that is being corrected.
        suggestions: list of suggestions.
        meta (dict, optinal): additional data associated with the annotation.

    """

    def __new__(cls, start, end, source_text, suggestions, meta=DEFAULT):

        if meta is DEFAULT:
            meta = {}
        return super().__new__(cls, start, end, source_text, suggestions, meta)

    def __hash__(self):
        return hash(
            (
                self.start,
                self.end,
                self.source_text,
                tuple(self.suggestions),
                tuple(self.meta.items()),
            )
        )

    def __eq__(self, other):
        return (
            self.start == other.start
            and self.end == other.end
            and self.source_text == other.source_text
            and tuple(self.suggestions) == tuple(other.suggestions)
            and tuple(sorted(self.meta.items()))
            == tuple(sorted(other.meta.items()))
        )

    @property
    def top_suggestion(self):
        """Return the first suggestion or None if there are none. """

        return self.suggestions[0] if self.suggestions else None

    def to_str(self, *, with_meta=True):
        """Return a string representation of the annotation.

        Example:
            >>> ann = Annotation(0, 4, 'helo', ['hello', 'hola'])
            >>> ann.to_str()
            '{helo=>hello|hola}'

        """
        if self.suggestions:
            repl = "|".join(self.suggestions)
        else:
            repl = NO_SUGGESTIONS

        meta_text = self._format_meta() if with_meta else ""
        return "{%s=>%s%s}" % (
            _escape(self.source_text),
            _escape(repl),
            meta_text)

    def _format_meta(self):
        return "".join(":::{}={}".format(k, v) for k, v in self.meta.items())


def span_intersect(spans, begin, end):
    """Check if interval [begin, end) intersects with any of given spans.

    Args:
        spans: list of (begin, end) pairs.
        begin (int): starting position of the query interval.
        end (int): ending position of the query interval.

    Return:
        Index of a span that intersects with [begin, end),
            or -1 if no such span exists.
    """

    def strictly_inside(a, b, x, y):
        """Test that first segment is strictly inside second one. """
        return x < a <= b < y

    for index, (b, e) in enumerate(spans):
        overlap = max(0, min(end, e) - max(begin, b))
        if overlap:
            return index
        if strictly_inside(b, e, begin, end):
            return index
        if strictly_inside(begin, end, b, e):
            return index

    return -1




if __name__ == "__main__":
    import doctest

    doctest.testmod()

