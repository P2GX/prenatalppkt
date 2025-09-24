"""
biometry.py

Class-based implementation of prenatal biometric measurements.
Supports percentile calculation and mapping to ontology terms.
"""

from statistics import NormalDist
from dataclasses import dataclass
from typing import Optional
from . import constants


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

    def percentile_and_hpo(self) -> tuple[float, Optional[str]]:
        """
        Calculate the percentile and infer an ontology term if abnormal.

        Returns
        -------
        tuple[float, str | None]
            Percentile (0-100), and HPO identifier if abnormal, else None.

        Raises
        ------
        ValueError
            If the gestational age is invalid or reference data is missing.
        """
        if self.gestational_age_weeks < 12 or self.gestational_age_weeks > 40:
            raise ValueError(
                f"Unsupported gestational age: {self.gestational_age_weeks} weeks. "
                "Valid range is 12-40 weeks."
            )

        ref_table = _MOCK_REFERENCES.get(self.measurement_type, {})
        if self.gestational_age_weeks not in ref_table:
            raise ValueError(
                f"No reference data for {self.measurement_type} at "
                f"{self.gestational_age_weeks} weeks."
            )

        ref = ref_table[self.gestational_age_weeks]
        mean, sd = ref["mean"], ref["sd"]

        z_score = (self.value_mm - mean) / sd
        percentile = round(NormalDist().cdf(z_score) * 100, 1)

        if self.measurement_type == BiometryType.HEAD_CIRCUMFERENCE:
            if percentile < 3:
                return percentile, constants.HPO_MICROCEPHALY
            if percentile > 97:
                return percentile, constants.HPO_MACROCEPHALY

        return percentile, None
