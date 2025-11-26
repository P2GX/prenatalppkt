"""
Biometry data models for ETL pipeline.

Represents extracted biometry measurements with standardized naming.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, List, Dict

from prenatalppkt.gestational_age import GestationalAge

if TYPE_CHECKING:
    pass


@dataclass
class Biometry:
    """
    Represents a single biometry measurement.

    All linear measurements normalized to millimeters.
    All percentiles normalized to float (0-100 range).
    """

    name: str  # e.g., "HC", "BPD", "AC", "Femur"
    value_mm: float  # Always in millimeters
    percentile: Optional[float] = None  # 0-100 scale
    gestational_age: Optional["GestationalAge"] = None  # GestationalAge object
    method: Optional[str] = None  # e.g., "Hadlock", "Chervenak"
    fetus_number: Optional[int] = None

    def __post_init__(self):
        """Validate biometry data."""
        if self.value_mm <= 0:
            raise ValueError(f"Biometry value must be positive, got {self.value_mm}")

        if self.percentile is not None:
            if not 0 <= self.percentile <= 100:
                raise ValueError(f"Percentile must be 0-100, got {self.percentile}")


@dataclass
class BiometryCollection:
    """
    Collection of biometry measurements for a single fetus.

    Provides convenient lookup by measurement name.
    """

    measurements: List[Biometry]
    fetus_number: Optional[int] = None

    def get(self, name: str) -> Optional[Biometry]:
        """Get biometry measurement by name (case-insensitive)."""
        name_lower = name.lower()
        for m in self.measurements:
            if m.name.lower() == name_lower:
                return m
        return None

    def get_all(self, name: str) -> List[Biometry]:
        """Get all biometry measurements matching name (case-insensitive)."""
        name_lower = name.lower()
        return [m for m in self.measurements if m.name.lower() == name_lower]

    def to_dict(self) -> Dict[str, Biometry]:
        """Convert to dictionary keyed by measurement name."""
        return {m.name: m for m in self.measurements}

    @property
    def count(self) -> int:
        """Number of measurements in collection."""
        return len(self.measurements)

    @property
    def names(self) -> List[str]:
        """List of all measurement names in collection."""
        return [m.name for m in self.measurements]
