"""
src/prenatalppkt/parser/observer/fetus/fetus_ratios_parser.py

Parser for fetal biometric ratios such as HC/AC, FL/AC, FL/BPD, etc.
Each ratio includes its calculated percentile, range, and report flag.
"""

import logging
import typing
from prenatalppkt.dto.ratios_data import FetusRatiosData, Ratio

logger = logging.getLogger(__name__)


class FetusRatiosParser:
    """
    Parser for the 'ratios' section of the fetus JSON.
    Converts ratio entries into structured FetusRatiosData.
    """

    def _parse_ratio_entry(self, entry: dict) -> typing.Optional[Ratio]:
        """
        Safely parse a single ratio entry.
        Returns a Ratio object, or None if malformed.
        """
        try:
            return Ratio(
                label=entry.get("label"),
                value=float(entry.get("value", 0)),
                decimal_places=int(entry.get("decimal_paces", 0)),
                calculated_percentile=float(entry.get("calculated_percentile", 0)),
                percentile_for_display=entry.get("percentile_for_display", ""),
                print_in_report=bool(entry.get("print_in_report", 0)),
                range_str=entry.get("range", ""),
                fetus_number=int(entry.get("fetus_number", 0)),
            )
        except Exception as e:
            logger.warning("Skipping malformed ratio entry: %s", e)
            return None

    def parse(
        self, json_data: typing.Dict[str, object]
    ) -> typing.Optional[FetusRatiosData]:
        """
        Parse the 'ratios' array from the JSON.
        Returns a FetusRatiosData instance or None if not found.
        """
        if not isinstance(json_data, dict):
            raise ValueError(
                f"Malformed argument: expected dict but got {type(json_data)}"
            )

        ratios = json_data.get("ratios")
        if not ratios:
            logger.info("No 'ratios' key found or empty list in fetus JSON")
            return None

        parsed_ratios = [r for r in (self._parse_ratio_entry(r) for r in ratios) if r]

        fetus_number = parsed_ratios[0].fetus_number if parsed_ratios else None

        logger.debug(
            "Parsed %d ratios for fetus_number=%s", len(parsed_ratios), fetus_number
        )

        return FetusRatiosData(fetus_number=fetus_number, ratios=parsed_ratios)
