"""
src/prenatalppkt/dto/ratios_data.py

Data Transfer Object for fetal biometric ratios (e.g., HC/AC, FL/BPD)
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Ratio:
    """Individual biometric ratio entry."""

    label: str
    value: float
    decimal_places: int
    calculated_percentile: float
    percentile_for_display: str
    print_in_report: bool
    range_str: str
    fetus_number: int


@dataclass
class FetusRatiosData:
    """
    Collection of fetal biometric ratios for a given fetus.
    """

    fetus_number: Optional[int]
    ratios: List[Ratio]

    @property
    def ratio_count(self) -> int:
        """Return the number of ratio entries."""
        return len(self.ratios)

    def get_ratio_by_label(self, label: str) -> Optional[Ratio]:
        """Retrieve a ratio by label (case-insensitive)."""
        for r in self.ratios:
            if r.label.lower() == label.lower():
                return r
        return None
