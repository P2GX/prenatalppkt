import logging
import typing
from prenatalppkt.hpo import HpoConceptRecognizer
from prenatalppkt.dto import FetusData
from prenatalppkt.parser.observer.fetus.fetus_anatomy_text_parser import (
    FetusAnatomyTextParser,
)
from prenatalppkt.parser.observer.fetus.fetus_fetus_parser import FetusFetusParser
from prenatalppkt.parser.observer.fetus.fetus_measurements_parser import (
    FetusMeasurementsParser,
)


logger = logging.getLogger(__name__)

"""
Initial parser for the the "fetus" superfield within the Observer JSON

Will be extended/adapted to be a container for all parsers which handle sub-"fetus" fields
"""


class FetusParser:
    """Main parser for a single fetus JSON object."""

    def __init__(self, hcr: HpoConceptRecognizer):
        self._hcr = hcr
        self._anatomy_parser = FetusAnatomyTextParser(hcr)
        self._fetus_parser = FetusFetusParser(hcr)
        self._measurements_parser = FetusMeasurementsParser()

    def parse(self, json_data: typing.Dict[str, object]) -> FetusData:
        """
        Parse the fetus JSON block into a FetusData object that combines
        anatomy (HPO terms), fetal attributes, and quantitative measurements.
        """
        if not isinstance(json_data, dict):
            raise ValueError(
                f"malformed argument: expecting dict but got {type(json_data)}"
            )

        # --- Parse anatomy_text ---
        fetus_section = json_data.get("fetus")
        fetus_data_anatomy = None
        fetus_data_dict = None
        if fetus_section:
            # Parse general fetal metadata (number, growth, GA, gender, etc.)
            fetus_data_dict = self._fetus_parser.parse(fetus_section)

            # Parse the anatomy_text (for HPO concept extraction)
            try:
                fetus_data_anatomy = self._anatomy_parser.parse(fetus_section)
                logger.debug("Parsed anatomy_text successfully")
            except ValueError:
                logger.info("No 'anatomy_text' found in 'fetus' key in JSON")

        # --- Parse 'fetus' section ---
        fetus_section = json_data.get("fetus")
        fetus_data_dict = None
        if fetus_section:
            fetus_data_dict = self._fetus_parser.parse(fetus_section)
            logger.debug("Parsed fetus section")

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

        # --- Combine results into a single FetusData DTO ---
        # Merge results from anatomy_text, fetus section, and measurements
        fetus_data = FetusData(
            hpo_term_list=(
                fetus_data_anatomy.hpo_term_list if fetus_data_anatomy else []
            ),
            measurements=measurements_data,
            **(fetus_data_dict or {}),  # include parsed fetal attributes
        )

        logger.debug(
            "FetusParser complete: fetus_number=%s, measurements=%s",
            getattr(fetus_data, "fetus_number", None),
            getattr(measurements_data, "measurement_count", 0),
        )
        return fetus_data
