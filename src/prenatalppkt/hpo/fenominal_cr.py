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
