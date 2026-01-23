"""
src/prenatalppkt/parser/observer/fetus_parser.py

Main parser for a single fetus entry within the Observer JSON.

This acts as a coordinator that delegates parsing of the individual
subsections of the "fetuses" top-level key, assembling results into
semantically-grouped DTOs via the FetusDataBuilder.
"""

import typing
import logging

from prenatalppkt.dto.fetus_data import FetusData
from prenatalppkt.dto.observer.builders.fetus_data_builder import FetusDataBuilder
from prenatalppkt.dto.observer.fetuses.fetus_core_data import FetusCoreData
from prenatalppkt.dto.observer.builders.fetus_anatomy_data import FetusAnatomyData
from prenatalppkt.dto.observer.builders.fetus_biometry_data import FetusBiometryData
from prenatalppkt.parser.observer.fetuses.fetuses_anatomy_text_parser import (
    FetusAnatomyTextParser,
)
from prenatalppkt.parser.observer.fetuses.fetuses_fetus_parser import FetusFetusParser
from prenatalppkt.parser.observer.fetuses.fetuses_measurements_parser import (
    FetusMeasurementsParser,
)
from prenatalppkt.parser.observer.fetuses.fetuses_ratios_parser import FetusRatiosParser
from prenatalppkt.parser.observer.fetuses.fetuses_efw_parser import FetusEfwParser
from prenatalppkt.hpo import HpoConceptRecognizer

logger = logging.getLogger(__name__)


class FetusesParser:
    """Main parser for a single fetuses entry within the Observer JSON."""

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

    def _build_anatomy_data(
        self, json_data: typing.Dict[str, typing.Any], anatomy_text_result
    ) -> typing.Optional[FetusAnatomyData]:
        """Build FetusAnatomyData from parsed anatomy_text and raw JSON."""
        hpo_terms = anatomy_text_result.hpo_term_list if anatomy_text_result else []

        # Extract raw anatomy_text string from fetus section
        fetus_section = json_data.get("fetus", {})
        anatomy_text_str = fetus_section.get("anatomy_text")

        # Extract structured anatomy array
        anatomy_array = json_data.get("anatomy")

        # Extract impression data
        impression = json_data.get("impression")

        # Only create if we have any anatomy data
        if hpo_terms or anatomy_text_str or anatomy_array or impression:
            return FetusAnatomyData(
                hpo_terms=hpo_terms,
                anatomy_text=anatomy_text_str,
                anatomy=anatomy_array,
                impression=impression,
            )
        return None

    def _build_biometry_data(
        self, measurements_data, ratios_data, efw_data
    ) -> typing.Optional[FetusBiometryData]:
        """Build FetusBiometryData from parsed measurements, ratios, and EFWs."""
        if measurements_data or ratios_data or efw_data:
            return FetusBiometryData(
                measurements=measurements_data, ratios=ratios_data, efws=efw_data
            )
        return None

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

        # Parse fetus core info (required)
        fetus_core_dict = self._parse_section(
            self._fetus_parser, json_data.get("fetus", {}), "fetus", "fetus section"
        )

        if not fetus_core_dict:
            raise ValueError("Missing required 'fetus' section in JSON")

        fetus_core = FetusCoreData(**fetus_core_dict)

        # Parse anatomy text for HPO terms
        anatomy_text_result = self._parse_section(
            self._anatomy_parser,
            json_data.get("fetus", {}),
            "anatomy_text",
            "anatomy_text section",
        )

        # Build grouped anatomy data
        anatomy_data = self._build_anatomy_data(json_data, anatomy_text_result)

        # Parse biometry sub-sections
        measurements_data = self._parse_section(
            self._measurements_parser, json_data, "measurements", "measurements section"
        )

        ratios_data = self._parse_section(
            self._ratios_parser, json_data, "ratios", "ratios section"
        )

        efw_data = self._parse_section(
            self._efw_parser, json_data, "efws", "efws section"
        )

        # Build grouped biometry data
        biometry_data = self._build_biometry_data(
            measurements_data, ratios_data, efw_data
        )

        # Assemble FetusData using builder
        builder = FetusDataBuilder(fetus_core)

        if anatomy_data:
            builder.with_anatomy(anatomy_data)

        if biometry_data:
            builder.with_biometry(biometry_data)

        # Future: Add echo, procedures, environment, gestational when parsers exist
        # if echo_data:
        #     builder.with_echo(echo_data)

        fetus_data = builder.build()

        logger.debug(
            "FetusParser complete: fetus_number=%s, anatomy=%s, biometry=%s",
            fetus_core.fetus_number,
            anatomy_data is not None,
            biometry_data is not None,
        )

        return fetus_data
