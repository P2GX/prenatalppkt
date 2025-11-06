import logging
import typing
from prenatalppkt.hpo import HpoConceptRecognizer
from prenatalppkt.dto import FetusData

logger = logging.getLogger(__name__)


class FetusAnatomyTextParser:
   """Parses the 'anatomy_text' subfield within a fetus JSON object."""

   def __init__(self, hcr: HpoConceptRecognizer):
       self._hcr = hcr

   def parse(self, json_data: typing.Dict[str, object]) -> FetusData:
       """
       Parse the 'anatomy_text' subfield to extract HPO terms.

       Args:
           json_data: The fetus-level dictionary containing 'anatomy_text'

       Returns:
           FetusData: with extracted HPO terms
       """
       if "anatomy_text" not in json_data:
           raise ValueError("did not find 'anatomy_text' in fetus")

       anatomy_text = json_data.get("anatomy_text")
       hpo_hits = self._hcr.parse(anatomy_text)

       for hpo_hit in hpo_hits:
           logger.debug("HPO hit: %s", hpo_hit)

       return FetusData(hpo_term_list=hpo_hits)