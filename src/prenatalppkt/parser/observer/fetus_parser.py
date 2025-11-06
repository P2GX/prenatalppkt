"""
src/prenatalppkt/parser/observer/fetus_parser.py

Main parser for a single fetus entry within the Observer JSON.

This acts as a coordinator that delegates parsing of the individual
subsections of the "fetuses" top-level key, including:
- fetus: core fetal metadata (e.g., gender, GA, presentation)
- anatomy_text: qualitative HPO-annotated findings
- measurements: quantitative biometry
- ratios: computed biometric ratios (e.g., HC/AC)
- efws: estimated fetal weights

Each subsection is handled by a dedicated subparser, and the results
are assembled into a unified FetusData DTO.
"""

import logging
import typing
from prenatalppkt.hpo import HpoConceptRecognizer
from prenatalppkt.dto.fetus_data import FetusData
from prenatalppkt.parser.observer.fetus.fetus_anatomy_text_parser import (
   FetusAnatomyTextParser,
)
from prenatalppkt.parser.observer.fetus.fetus_fetus_parser import FetusFetusParser
from prenatalppkt.parser.observer.fetus.fetus_measurements_parser import (
   FetusMeasurementsParser,
)
from prenatalppkt.parser.observer.fetus.fetus_ratios_parser import FetusRatiosParser
from prenatalppkt.parser.observer.fetus.fetus_efw_parser import FetusEfwParser

logger = logging.getLogger(__name__)


class FetusParser:
   """Main parser for a single fetus JSON object."""

   def __init__(self, hcr: HpoConceptRecognizer):
       self._hcr = hcr
       self._anatomy_parser = FetusAnatomyTextParser(hcr)
       self._fetus_parser = FetusFetusParser(hcr)
       self._measurements_parser = FetusMeasurementsParser()
       self._ratios_parser = FetusRatiosParser()
       self._efw_parser = FetusEfwParser()

   # -------------------------------------------------------------------------
   # Core entry point
   # -------------------------------------------------------------------------

   def parse(self, json_data: typing.Dict[str, object]) -> FetusData:
       """
       Parse a single fetus JSON block into a FetusData object combining
       anatomy, core fetal attributes, measurements, ratios, and EFWs.

       Args:
           json_data: Dict representing a single fetus entry from the
                      "fetuses" list in Observer JSON.

       Returns:
           FetusData: Unified DTO for all fetal sections.
       """
       if not isinstance(json_data, dict):
           raise ValueError(
               f"Malformed argument: expecting dict but got {type(json_data)}"
           )

       fetus_section = json_data.get("fetus")
       fetus_core = None
       fetus_anatomy = None

       # ------------------------------------------------------------------
       # Parse the 'fetus' metadata section
       # ------------------------------------------------------------------
       if fetus_section:
           try:
               fetus_core = self._fetus_parser.parse(fetus_section)
               logger.debug("Parsed fetus core section successfully.")
           except Exception as e:
               logger.warning("Failed to parse fetus section: %s", e)

           # Parse anatomy text (optional)
           try:
               fetus_anatomy = self._anatomy_parser.parse(fetus_section)
               logger.debug("Parsed anatomy_text successfully.")
           except ValueError:
               logger.info("No 'anatomy_text' found in fetus section.")
           except Exception as e:
               logger.warning("Error parsing anatomy_text: %s", e)

       # ------------------------------------------------------------------
       # Parse 'measurements'
       # ------------------------------------------------------------------
       measurements_data = None
       if "measurements" in json_data:
           try:
               measurements_data = self._measurements_parser.parse(json_data)
               logger.debug(
                   "Parsed %d measurement entries.",
                   getattr(measurements_data, "measurement_count", 0),
               )
           except Exception as e:
               logger.warning("Failed to parse measurements: %s", e)

       # ------------------------------------------------------------------
       # Parse 'ratios'
       # ------------------------------------------------------------------
       ratios_data = None
       if "ratios" in json_data:
           try:
               ratios_data = self._ratios_parser.parse(json_data)
               logger.debug(
                   "Parsed %d ratio entries.", getattr(ratios_data, "ratio_count", 0)
               )
           except Exception as e:
               logger.warning("Failed to parse ratios: %s", e)

       # ------------------------------------------------------------------
       # Parse 'efws'
       # ------------------------------------------------------------------
       efw_data = None
       if "efws" in json_data:
           try:
               efw_data = self._efw_parser.parse(json_data)
               logger.debug(
                   "Parsed %d EFW entries.", getattr(efw_data, "efw_count", 0)
               )
           except Exception as e:
               logger.warning("Failed to parse EFW section: %s", e)

       # ------------------------------------------------------------------
       # Combine results
       # ------------------------------------------------------------------
       fetus_data = FetusData(
           hpo_term_list=(fetus_anatomy.hpo_term_list if fetus_anatomy else []),
           fetus=fetus_core,
           measurements=measurements_data,
           ratios=ratios_data,
           efws=efw_data,
           # other sections (placenta, nst, etc.) can be added later
       )

       logger.debug(
           "FetusParser complete: fetus_number=%s | "
           "measurements=%s | ratios=%s | efws=%s",
           getattr(fetus_core, "fetus_number", None),
           getattr(measurements_data, "measurement_count", 0)
           if measurements_data
           else None,
           getattr(ratios_data, "ratio_count", 0) if ratios_data else None,
           getattr(efw_data, "efw_count", 0) if efw_data else None,
       )

       return fetus_data