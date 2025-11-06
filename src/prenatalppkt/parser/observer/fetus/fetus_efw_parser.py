"""
src/prenatalppkt/parser/observer/fetus/fetus_efw_parser.py

Parser for the 'efws' section of the fetus JSON, handling Estimated Fetal Weight (EFW) entries.
"""

import logging
import typing
from prenatalppkt.dto.fetuses.efw_data import EfwEntry, FetusEfwData

logger = logging.getLogger(__name__)


class FetusEfwParser:
    """Parser for the 'efws' section within the fetus JSON."""

    def _parse_efw_entry(self, entry: dict) -> typing.Optional[EfwEntry]:
        """Safely parse a single EFW entry."""
        try:
            return EfwEntry(
                fetus_number=int(entry.get("fetus_number", 0)),
                label=entry.get("label", ""),
                value=float(entry.get("value", 0)),
                decimal_places=int(entry.get("decimal_places", 0)),
                calculated_percentile=float(entry.get("calculated_percentile", 0)),
                percentile_for_display=entry.get("percentile_for_display", ""),
                print_in_report=bool(entry.get("print_in_report", 0)),
                range_str=entry.get("range", ""),
            )
        except Exception as e:
            logger.warning("Skipping malformed EFW entry: %s", e)
            return None

    def parse(
        self, json_data: typing.Dict[str, object]
    ) -> typing.Optional[FetusEfwData]:
        """Parse the 'efws' list into FetusEfwData."""
        if not isinstance(json_data, dict):
            raise ValueError(
                f"Malformed argument: expected dict but got {type(json_data)}"
            )

        efws = json_data.get("efws")
        if not efws:
            logger.info("No 'efws' key found or empty list in fetus JSON")
            return None

        parsed_entries = [e for e in (self._parse_efw_entry(i) for i in efws) if e]

        fetus_number = parsed_entries[0].fetus_number if parsed_entries else None
        logger.debug(
            "Parsed %d EFW entries for fetus_number=%s",
            len(parsed_entries),
            fetus_number,
        )

        return FetusEfwData(fetus_number=fetus_number, efw_entries=parsed_entries)
