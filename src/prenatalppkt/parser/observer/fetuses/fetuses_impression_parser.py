"""
src/prenatalppkt/parser/observer/fetuses/fetuses_impression_parser.py

Parser for the 'impression' section within a fetus JSON object.
"""

import logging
from typing import Any, Dict, Optional

from prenatalppkt.dto.observer.fetuses.fetus_impression_data import FetusImpressionData

logger = logging.getLogger(__name__)


class FetusImpressionParser:
    """Parse the 'impression' subkey at the fetus level from Observer JSON."""

    def parse(self, json_data: Dict[str, Any]) -> Optional[FetusImpressionData]:
        """
        Parse impression content out of a fetus-level mapping.

        Args:
            json_data: a dict representing a fetus entry from Observer JSON

        Returns:
            FetusImpressionData when impression content is present, otherwise None.
        """
        if not isinstance(json_data, dict):
            raise ValueError(
                f"malformed argument, expecting `dict` but got {type(json_data)}"
            )

        impression = json_data.get("impression")
        if not impression:
            logger.info("No 'impression' key found in fetus JSON")
            return None

        fetus_number = None
        fetus_meta = json_data.get("fetus")
        if isinstance(fetus_meta, dict):
            fetus_number = fetus_meta.get("fetus_number")

        # If impression is a single string, normalize and return
        if isinstance(impression, str):
            text = impression.strip()
            if not text:
                return None
            return FetusImpressionData(fetus_number=fetus_number, impression_text=text)

        # If impression is a list, filter and return as list
        if isinstance(impression, list):
            items = [str(i).strip() for i in impression if str(i).strip()]
            if not items:
                return None
            return FetusImpressionData(fetus_number=fetus_number, impressions=items)

        # Fallback: coerce to string if possible
        try:
            text = str(impression).strip()
            if text:
                return FetusImpressionData(
                    fetus_number=fetus_number, impression_text=text
                )
        except Exception:
            logger.warning("Unable to coerce 'impression' to string: %r", impression)

        return None
