"""
src/prenatalppkt/hpo/composite_cr.py

Concept recognizer that chains multiple recognizers in order.
"""

import typing

from .hpo_cr import HpoConceptRecognizer
from .simple_term import SimpleTerm


class CompositeConceptRecognizer(HpoConceptRecognizer):
    """
    Try an ordered list of recognizers, in order, on the same text.

    An ordered chain, not a fixed primary/fallback pair - each recognizer
    only gets a chance if the ones before it didn't already produce a
    result. Covers any single recognizer, or any ordering/length of
    chain, with the same class.

    First-cut merge granularity is whole-text-level, not span-level: each
    recognizer runs against the full ``cell_contents``, and the first one to
    return any hits wins outright - there's no attempt to merge hits from
    different recognizers within the same text, or to combine a recognizer's
    partial hits with another's. Finer-grained (span-level) merging is a real,
    known future refinement, not attempted here until real benchmark data
    shows whole-text fallback isn't good enough.
    """

    def __init__(self, recognizers: typing.Sequence[HpoConceptRecognizer]) -> None:
        if not recognizers:
            raise ValueError("CompositeConceptRecognizer needs at least one recognizer")
        self._recognizers = list(recognizers)

    def parse(self, cell_contents, custom_d=None) -> typing.List[SimpleTerm]:
        """Try each recognizer in order; return the first non-empty result.

        If every recognizer returns no hits, returns the last recognizer's
        (empty) result.
        """
        result: typing.List[SimpleTerm] = []
        for recognizer in self._recognizers:
            result = recognizer.parse(cell_contents, custom_d)
            if result:
                return result
        return result
