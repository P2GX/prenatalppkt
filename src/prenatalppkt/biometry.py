"""
biometry.py

Class-based implementation of prenatal biometric measurements.
Supports percentile calculation and mapping to ontology terms.
"""

from dataclasses import dataclass
from .biometry_type import BiometryType
from typing import Optional
from .biometry_reference import FetalGrowthPercentiles


@dataclass
class BiometryMeasurement:
    """
    Represents a single prenatal biometric measurement.

    Attributes
    ----------
    measurement_type : BiometryType
        The type of measurement, e.g., BiometryType.HEAD_CIRCUMFERENCE.
    gestational_age_weeks : float
        Gestational age in completed weeks.
    value_mm : float
        Measurement value in millimeters.
    """

    measurement_type: BiometryType
    gestational_age_weeks: float
    value_mm: float

    def percentile_and_hpo(
        self, reference: Optional[FetalGrowthPercentiles] = None
    ) -> tuple[float, Optional[str]]:
        """
        Calculate the percentile and infer an ontology term if abnormal.

        NOTE: This method is deprecated. Use MeasurementEvaluation instead.
        HPO mapping now handled by the new data-driven architecture.

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

        # Simple thresholds for backwards compatibility
        # For full HPO mapping, use MeasurementEvaluation
        if percentile <= 3 or percentile >= 97:
            # Return basic abnormal indicator
            return percentile, "ABNORMAL"

        return percentile, None
