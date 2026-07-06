"""
src/prenatalppkt/hpo/fenominal_cr.py

Concept recognizer backed by the fenominal text -> HPO engine.
"""

import json
import typing

from fenominal import Fenominal

from .hpo_cr import HpoConceptRecognizer
from .simple_term import SimpleTerm


class FenominalConceptRecognizer(HpoConceptRecognizer):
    """
    Recognize HPO concepts in free text using fenominal.

    fenominal reads an existing ``hp.json`` (it never downloads) and returns one
    hit per recognized term with keys ``termId``, ``label``, ``span`` and
    ``excluded``; the ``excluded`` flag carries fenominal's negation detection.
    """

    def __init__(self, hp_json_path: str) -> None:
        self._fenominal = Fenominal(hp_json_path)

    def parse(self, cell_contents, custom_d=None) -> typing.List[SimpleTerm]:
        """Recognize HPO terms in free text via fenominal.

        ``custom_d`` is accepted for interface compatibility but ignored;
        fenominal performs recognition itself. Each hit's ``excluded`` flag is
        carried straight onto the returned SimpleTerm.
        """
        text = str(cell_contents).replace("\n", " ")
        hits = json.loads(self._fenominal.map_text(text))
        return [
            SimpleTerm(
                hpo_id=hit["termId"], hpo_label=hit["label"], excluded=hit["excluded"]
            )
            for hit in hits
        ]

    def parse_cell_for_exact_matches(
        self, cell_contents, custom_d
    ) -> typing.List[SimpleTerm]:
        """Not supported: fenominal has no custom-dictionary exact-match mode."""
        # TODO(varenya): decide if custom-dictionary matching can be rebuilt on
        # fenominal, or dropped; unused by any caller today. See the Part 3 follow-up.
        raise NotImplementedError(
            "FenominalConceptRecognizer does not support custom-dictionary matching"
        )

    def get_term_from_id(self, hpo_id) -> SimpleTerm:
        """Not supported: fenominal recognizes text, it does not look terms up by id."""
        # TODO(varenya): decide if id lookup can be rebuilt on fenominal, or
        # dropped; unused by any caller today. See the Part 3 follow-up.
        raise NotImplementedError(
            "FenominalConceptRecognizer does not support id lookup"
        )

    def get_term_from_label(self, label) -> SimpleTerm:
        """Not supported: fenominal recognizes text, it does not look terms up by label."""
        # TODO(varenya): decide if label lookup can be rebuilt on fenominal, or
        # dropped; unused by any caller today. See the Part 3 follow-up.
        raise NotImplementedError(
            "FenominalConceptRecognizer does not support label lookup"
        )
