"""
src/prenatalppkt/dto/observer/fetuses/fetus_impression_data.py

DTO for fetus impression(s) extracted from Observer JSON.
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Dict


@dataclass
class FetusImpressionData:
    """
    Data class representing impression information attached to a fetus entry.

    Attributes:
        fetus_number: optional numeric fetus identifier
        impression_text: raw impression string when a single string is present
        impressions: list of impression items when it's structured as a list
        fetus_anomalies: list of anomaly dictionaries
        other: any other impression-related data
    """

    fetus_number: Optional[int] = None
    impression_text: Optional[str] = None
    impressions: Optional[List[str]] = None
    fetus_anomalies: Optional[List[Dict[str, Any]]] = None
    other: Optional[Dict[str, Any]] = None

    @property
    def is_present(self) -> bool:
        """Return True if any impression content is present."""
        return bool(
            self.impression_text
            or (self.impressions and len(self.impressions) > 0)
            or self.fetus_anomalies
            or self.other
        )

    def __repr__(self) -> str:
        return f"FetusImpressionData(fetus_number={self.fetus_number}, present={self.is_present})"

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FetusImpressionData":
        """
        Create FetusImpressionData from a dictionary.

        Args:
            d: Dictionary containing impression data

        Returns:
            FetusImpressionData instance
        """
        return cls(
            fetus_anomalies=d.get("fetus_anomalies"),
            other={k: v for k, v in d.items() if k not in {"fetus_anomalies"}},
        )
