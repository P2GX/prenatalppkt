import logging
import typing
from prenatalppkt.hpo import HpoConceptRecognizer
from prenatalppkt.dto import FetusData

logger = logging.getLogger(__name__)

"""
Initial parser for the the "fetus" superfield within the Observer JSON

Will be extended/adapted to be a container for all parsers which handle sub-"fetus" fields

Currently handles the "anatomy_text" subfield
"""


class FetusParser:
    """
    Parser for high-level fetus JSON block
    """

    def __init__(self, hcr: HpoConceptRecognizer):
        self._hcr = hcr

    def parse(self, json_data: typing.Dict[str, object]) -> FetusData:
        """
        Convert JSON to FetusData instance with parsed HPO terms
        """
        if not isinstance(json_data, dict):
            raise ValueError(
                f"malformed arguement, expecting `dict` but got {type(json_data)}"
            )

        if "anatomy_text" not in json_data:
            raise ValueError("did not find 'anatomy_text' in fetus")

        anatomy_text = json_data.get("anatomy_text")

        # first_name = patient.get('first_name', "NA")
        for hpo_hit in self._hcr.parse(anatomy_text):
            logger.debug("HPO hit: %s", hpo_hit)

        hpo_hits = self._hcr.parse(anatomy_text)

        return FetusData(hpo_term_list=hpo_hits)
