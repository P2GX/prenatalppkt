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

Each subsection is handled by a dedicated subparser, and the results are assembled into a unified FetusData Data Transfer Object.
"""

import typing
import logging

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
from prenatalppkt.hpo import HpoConceptRecognizer

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
    # Private helpers
    # -------------------------------------------------------------------------

    def _parse_section(
        self,
        parser: typing.Any,
        json_data: typing.Optional[typing.Dict[str, typing.Any]],
        key: str,
        log_name: str,
    ) -> typing.Optional[typing.Any]:
        """
        Generic helper to safely parse a section and handle errors gracefully.
        """
        section_data = None
        if not json_data:
            logger.debug("No data found for section '%s'", log_name)
            return None

        try:
            section_data = parser.parse(json_data)
            logger.debug("Parsed %s successfully", log_name)
        except Exception as e:
            logger.warning("Failed to parse %s: %s", log_name, e)

        return section_data

    # -------------------------------------------------------------------------
    # Public entry point
    # -------------------------------------------------------------------------

    def parse(self, json_data: typing.Dict[str, typing.Any]) -> FetusData:
        """
        Parse a single fetus JSON block into a FetusData object combining
        anatomy, measurements, ratios, and efw data.
        """
        if not isinstance(json_data, dict):
            raise ValueError(
                f"Malformed argument: expected dict but got {type(json_data)}"
            )

        # Parse fetus core info
        fetus_info_data = self._parse_section(
            self._fetus_parser, json_data.get("fetus", {}), "fetus", "fetus section"
        )

        # Parse anatomy text
        anatomy_data = self._parse_section(
            self._anatomy_parser,
            json_data.get("fetus", {}),
            "anatomy_text",
            "anatomy_text section",
        )

        # Parse sub-sections directly under fetus
        measurements_data = self._parse_section(
            self._measurements_parser, json_data, "measurements", "measurements section"
        )

        ratios_data = self._parse_section(
            self._ratios_parser, json_data, "ratios", "ratios section"
        )

        efw_data = self._parse_section(
            self._efw_parser, json_data, "efws", "efws section"
        )

        # Assemble unified FetusData
        fetus_data = FetusData(
            hpo_term_list=(anatomy_data.hpo_term_list if anatomy_data else []),
            measurements=measurements_data,
            ratios=ratios_data,
            efws=efw_data,
            **(fetus_info_data or {}),
        )

        logger.debug(
            "FetusParser complete: fetus_number=%s, measurements=%s, ratios=%s, efws=%s",
            getattr(fetus_data, "fetus_number", None),
            getattr(measurements_data, "measurement_count", 0)
            if measurements_data
            else None,
            getattr(ratios_data, "ratio_count", 0) if ratios_data else None,
            getattr(efw_data, "efw_count", 0) if efw_data else None,
        )

        return fetus_data
