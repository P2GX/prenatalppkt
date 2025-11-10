"""
src/prenatalppkt/parser/observer/fetus/fetus_anatomy_text_parser.py

Parser for extracting HPO terms from anatomy_text field in Observer JSON.
"""

import logging
import typing
from dataclasses import dataclass
from prenatalppkt.hpo.simple_term import SimpleTerm

logger = logging.getLogger(__name__)


@dataclass
class AnatomyTextResult:
    """Result from parsing anatomy_text, containing extracted HPO terms."""

    hpo_term_list: typing.List[SimpleTerm]


class FetusAnatomyTextParser:
    """
    Parser for anatomy_text field within the fetus JSON.
    Extracts HPO phenotype terms using an HPO concept recognizer.
    """

    def __init__(self, hpo_concept_recognizer):
        """
        Initialize with an HPO concept recognizer.

        Args:
            hpo_concept_recognizer: Tool for extracting HPO terms from text
        """
        self._hcr = hpo_concept_recognizer

    def parse(self, json_data: typing.Dict[str, object]) -> AnatomyTextResult:
        """
        Parse the 'anatomy_text' subfield to extract HPO terms.

        Args:
            json_data: The fetus-level dictionary containing 'anatomy_text'

        Returns:
            AnatomyTextResult: with extracted HPO terms
        """
        if "anatomy_text" not in json_data:
            raise ValueError("did not find 'anatomy_text' in fetus")

        anatomy_text = json_data.get("anatomy_text")
        hpo_hits = self._hcr.parse(anatomy_text)

        for hpo_hit in hpo_hits:
            logger.debug("HPO hit: %s", hpo_hit)

        return AnatomyTextResult(hpo_term_list=hpo_hits)
