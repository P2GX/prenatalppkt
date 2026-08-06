"""
src/prenatalppkt/hpo/ferrific_cr.py

Concept recognizer backed by the ferrific text -> HPO engine.
"""

import typing

from .hpo_cr import HpoConceptRecognizer
from .simple_term import SimpleTerm


class FerrificConceptRecognizer(HpoConceptRecognizer):
    """
    Recognize HPO concepts in free text using ferrific.

    ferrific reads an existing ``hp.json`` (it never downloads) and returns native
    ``Hit`` objects with ``term_id``, ``label``, ``span`` and ``excluded``
    attributes - no JSON round trip needed, unlike ``FenominalConceptRecognizer``.
    Uses ``map_text_longest`` (containment-filtered, one hit per span) rather than
    ``map_text``'s default of returning every overlapping candidate, to match the
    non-overlapping output shape every other recognizer in this module produces.
    """

    def __init__(self, hp_json_path: str) -> None:
        # Imported here, not at module level, so importing this module never
        # requires ferrific to be installed unless this class is actually
        # instantiated.
        from ferrific import Ferrific

        self._ferrific = Ferrific(hp_json_path)

    def parse(self, cell_contents, custom_d=None) -> typing.List[SimpleTerm]:
        """Recognize HPO terms in free text via ferrific.

        ``custom_d`` is accepted for interface compatibility but ignored;
        ferrific performs recognition itself. Each hit's ``excluded`` flag is
        carried straight onto the returned SimpleTerm.
        """
        text = str(cell_contents).replace("\n", " ")
        hits = self._ferrific.map_text_longest(text)
        return [
            SimpleTerm(hpo_id=hit.term_id, hpo_label=hit.label, excluded=hit.excluded)
            for hit in hits
        ]
