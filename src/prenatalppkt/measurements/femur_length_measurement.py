"""
femur_length_measurement.py

Defines `FemurLengthMeasurement`, a subclass of `SonographicMeasurement`
for fetal femur length (FL) evaluation.

This class provides a consistent interface for percentile evaluation
without embedding any reference data directly.  Actual reference tables
will be injected via parsing utilities in a future PR.
"""

from __future__ import annotations
from prenatalppkt.sonographic_measurement import SonographicMeasurement


class FemurLengthMeasurement(SonographicMeasurement, measurement_type="femur_length"):
    """
    Represents a sonographic measurement of fetal femur length (FL).

    Responsibilities
    ----------------
    - Provides a canonical measurement name.
    - Defines a placeholder for ontology mapping.
    - Delegates percentile evaluation logic to the superclass.
    """

    def __init__(self) -> None:
        """Initialize femur length measurement."""
        super().__init__()

    def name(self) -> str:
        """Return the canonical name for this measurement."""
        return "femur length"
