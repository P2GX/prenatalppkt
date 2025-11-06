"""
src/prenatalppkt/dto/fetuses/measurements_data.py
Data Transfer Object for fetal measurements.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Measurement:
    """
    Individual biometric measurement.

    Attributes:
        label: Measurement type (e.g., "AC", "BPD", "HC", "Femur")
        value: Measured value (in unit_of_measure)
        decimal_places: Number of decimal places used for display
        unit_of_measure: Unit (typically "cm")
        calculated_ega: Estimated gestational age from this measurement
        calculated_percentile: Percentile value (0-100)
        percentile_for_display: Display-friendly percentile string (e.g., "56%")
        include_in_avg_ga_calc: Whether this measurement contributes to GA average
        print_in_report: Whether measurement is printed in the ultrasound report
        calculated_z_score: Z-score for deviation from mean
        fetus_number: Fetus identifier
    """

    label: str
    value: float
    decimal_places: int = 0
    unit_of_measure: str = ""
    calculated_ega: float = 0.0
    calculated_percentile: float = 0.0
    percentile_for_display: str = ""
    include_in_avg_ga_calc: bool = True
    print_in_report: bool = True
    calculated_z_score: float = 0.0
    fetus_number: int = 0


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
