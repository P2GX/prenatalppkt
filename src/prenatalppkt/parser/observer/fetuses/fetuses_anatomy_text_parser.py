"""
src/prenatalppkt/parser/observer/fetuses/fetuses_anatomy_text_parser.py

Parses the 'anatomy_text' subfield within a fetus JSON object.
"""

import logging
import typing
from prenatalppkt.hpo import HpoConceptRecognizer
from prenatalppkt.hpo.simple_term import SimpleTerm

logger = logging.getLogger(__name__)


class FetusAnatomyTextParser:
    """Parses the 'anatomy_text' subfield within a fetus JSON object."""

    def __init__(self, hcr: HpoConceptRecognizer):
        self._hcr = hcr

    def parse(self, json_data: typing.Dict[str, object]) -> typing.Dict[str, object]:
        """
        Parse the 'anatomy_text' subfield to extract HPO terms.

        Args:
            json_data: The fetus-level dictionary containing 'anatomy_text'

        Returns:
            Dict with 'hpo_hits' key containing list of SimpleTerm objects
        """
        if "anatomy_text" not in json_data:
            raise ValueError("did not find 'anatomy_text' in fetus")

        anatomy_text = json_data.get("anatomy_text")
        simple_hits: typing.List[SimpleTerm] = self._hcr.parse(
            anatomy_text
        )  # Changed from parse_cell

        for hit in simple_hits:
            logger.debug("HPO hit: %s", hit)

        return {"hpo_hits": simple_hits}  # Returns SimpleTerm objects, not dicts
