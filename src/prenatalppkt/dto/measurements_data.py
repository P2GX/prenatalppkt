"""
src/prenatalppkt/dto/measurements_data.py
Data Transfer Object for fetal measurements
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Measurement:
    """
    Individual biometric measurement.

    Attributes:
        label: Measurement type (e.g., "AC", "BPD", "HC", "Femur")
        value: Measured value
        unit_of_measure: Unit (typically "cm")
        calculated_percentile: Percentile value (0-100)
        calculated_z_score: Z-score value
        calculated_ega: Estimated gestational age from this measurement
        fetus_number: Fetus identifier
    """

    label: str
    value: float
    unit_of_measure: str
    calculated_percentile: float
    calculated_z_score: float
    calculated_ega: float
    fetus_number: int


@dataclass
class MeasurementsData:
    """
    Collection of measurements for a fetus.

    Attributes:
        fetus_number: Fetus identifier
        measurements: List of Measurement objects
    """

    fetus_number: int
    measurements: List[Measurement]

    def get_measurement_by_label(self, label: str) -> Optional[Measurement]:
        """Get a specific measurement by its label (case-insensitive)."""
        for m in self.measurements:
            if m.label.lower() == label.lower():
                return m
        return None

    @property
    def measurement_count(self) -> int:
        """Total number of measurements."""
        return len(self.measurements)
