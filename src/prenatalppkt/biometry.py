"""
biometry.py

Class-based implementation of prenatal biometric measurements.
Supports percentile calculation and mapping to ontology terms.
"""

from dataclasses import dataclass
from typing import Optional
from . import constants
from .biometry_reference import FetalGrowthPercentiles


class BiometryType:
    """Types of biometric measurements supported by this library."""

    HEAD_CIRCUMFERENCE = "head_circumference"
    BIPARIETAL_DIAMETER = "biparietal_diameter"
    ABDOMINAL_CIRCUMFERENCE = "abdominal_circumference"
    FEMUR_LENGTH = "femur_length"
    ESTIMATED_FETAL_WEIGHT = "estimated_fetal_weight"


# Mock reference data for demonstration purposes.
# Only head circumference at 20 weeks is currently supported.
_MOCK_REFERENCES = {
    BiometryType.HEAD_CIRCUMFERENCE: {
        20: {"mean": 175.0, "sd": 10.0}  # millimeters
    }
}


@dataclass
class BiometryMeasurement:
    """
    Represents a single prenatal biometric measurement.

    Attributes
    ----------
    measurement_type : str
        The type of measurement, e.g., BiometryType.HEAD_CIRCUMFERENCE.
    gestational_age_weeks : float
        Gestational age in completed weeks.
    value_mm : float
        Measurement value in millimeters.
    """

    measurement_type: str
    gestational_age_weeks: float
    value_mm: float

    def percentile_and_hpo(
        self, reference: Optional[FetalGrowthPercentiles] = None
    ) -> tuple[float, Optional[str]]:
        """
        Calculate the percentile and infer an ontology term if abnormal.

        Parameters
        ----------
        reference : FetalGrowthPercentiles, optional
            Reference growth standard to use. If None, raises ValueError.

        Returns
        -------
        tuple[float, str | None]
            Percentile (0-100), and HPO identifier if abnormal, else None.

        Raises
        ------
        ValueError
            If no reference is provided, gestational age is invalid,
            or the measurement type is unsupported by the reference.
        """
        if reference is None:
            raise ValueError("A FetalGrowthPercentiles reference must be provided.")

        percentile = reference.lookup_percentile(
            measurement_type=self.measurement_type,
            gestational_age_weeks=self.gestational_age_weeks,
            value_mm=self.value_mm,
        )

        # Abnormal thresholds (<=3rd or >=97th percentile) by measurement
        if self.measurement_type == BiometryType.HEAD_CIRCUMFERENCE:
            if percentile <= 3:
                return percentile, constants.HPO_MICROCEPHALY
            if percentile >= 97:
                return percentile, constants.HPO_MACROCEPHALY

        if self.measurement_type == BiometryType.FEMUR_LENGTH:
            if percentile <= 3:
                return percentile, constants.HPO_SHORT_FEMUR
            if percentile >= 97:
                return percentile, constants.HPO_LONG_FEMUR

        return percentile, None
