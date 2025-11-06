import logging
import typing
from prenatalppkt.hpo import HpoConceptRecognizer
from prenatalppkt.dto import FetusData
from prenatalppkt.parser.observer.fetus.fetus_anatomy_text_parser import FetusAnatomyTextParser
from prenatalppkt.parser.observer.fetus.fetus_fetus_parser import FetusFetusParser
from prenatalppkt.parser.observer.fetus.fetus_measurements_parser import FetusMeasurementsParser
from prenatalppkt.parser.observer.fetus.fetus_ratios_parser import FetusRatiosParser
from prenatalppkt.parser.observer.fetus.fetus_efw_parser import FetusEfwParser

logger = logging.getLogger(__name__)

"""
Initial parser for the "fetus" superfield within the Observer JSON.

This serves as a coordinator, delegating to sub-parsers that handle:
- anatomy_text (qualitative findings)
- fetus (basic attributes)
- measurements (quantitative biometry)
- ratios (computed biometric ratios)
"""


class FetusParser:
   """Main parser for a single fetus JSON object."""

   def __init__(self, hcr: HpoConceptRecognizer):
       self._hcr = hcr
       self._anatomy_parser = FetusAnatomyTextParser(hcr)
       self._fetus_parser = FetusFetusParser(hcr)
       self._measurements_parser = FetusMeasurementsParser()
       self._ratios_parser = FetusRatiosParser()
       self._efw_parser = FetusEfwParser()

   def parse(self, json_data: typing.Dict[str, object]) -> FetusData:
       """
       Parse the fetus JSON block into a FetusData object combining
       anatomy (HPO terms), fetal attributes, measurements, and ratios.
       """
       if not isinstance(json_data, dict):
           raise ValueError(
               f"Malformed argument: expecting dict but got {type(json_data)}"
           )

       fetus_section = json_data.get("fetus")
       fetus_data_dict = None
       fetus_data_anatomy = None

       # --- Parse 'fetus' metadata section ---
       if fetus_section:
           try:
               fetus_data_dict = self._fetus_parser.parse(fetus_section)
               logger.debug("Parsed fetus section")
           except Exception as e:
               logger.warning("Failed to parse fetus section: %s", e)

           # --- Parse anatomy_text ---
           try:
               fetus_data_anatomy = self._anatomy_parser.parse(fetus_section)
               logger.debug("Parsed anatomy_text successfully")
           except ValueError:
               logger.info("No 'anatomy_text' found in 'fetus' key in JSON")
           except Exception as e:
               logger.warning("Error parsing anatomy_text: %s", e)

       # --- Parse 'measurements' section ---
       measurements_data = None
       if "measurements" in json_data:
           try:
               measurements_data = self._measurements_parser.parse(json_data)
               logger.debug(
                   "Parsed measurements (%d items)",
                   measurements_data.measurement_count,
               )
           except Exception as e:
               logger.warning("Failed to parse measurements: %s", e)

       # --- Parse 'ratios' section ---
       ratios_data = None
       if "ratios" in json_data:
           try:
               ratios_data = self._ratios_parser.parse(json_data)
               logger.debug(
                   "Parsed ratios (%d items)", getattr(ratios_data, "ratio_count", 0)
               )
           except Exception as e:
               logger.warning("Failed to parse ratios: %s", e)
       # --- Parse 'efws' section ---
       efw_data = None
       if "efws" in json_data:
           try:
               efw_data = self._efw_parser.parse(json_data)
               logger.debug(
                   "Parsed EFW entries (%d items)",
                   getattr(efw_data, "efw_count", 0),
               )
           except Exception as e:
               logger.warning("Failed to parse EFW section: %s", e)


       # --- Combine all results into a single FetusData DTO ---
       fetus_data = FetusData(
           hpo_term_list=(fetus_data_anatomy.hpo_term_list if fetus_data_anatomy else []),
           measurements=measurements_data,
           ratios=ratios_data,
           efw=efw_data,
           **(fetus_data_dict or {}),
       )

       logger.debug(
           "FetusParser complete: fetus_number=%s, measurements=%s, ratios=%s",
           getattr(fetus_data, "fetus_number", None),
           getattr(measurements_data, "measurement_count", 0)
           if measurements_data
           else None,
           getattr(ratios_data, "ratio_count", 0) if ratios_data else None,
           getattr(efw_data, "efw_count", 0) if efw_data else None,
       )

       return fetus_data