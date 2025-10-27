"""
head_circumference_measurement.py

Defines `HeadCircumferenceMeasurement`, a subclass of `SonographicMeasurement`
for fetal head circumference (HC) evaluation.

Automatically registered under `"head_circumference"`.
"""

from __future__ import annotations
from prenatalppkt.sonographic_measurement import SonographicMeasurement
from prenatalppkt.biometry_type import BiometryType


class HeadCircumferenceMeasurement(
    SonographicMeasurement, measurement_type=BiometryType.HEAD_CIRCUMFERENCE
):
    """Represents a sonographic measurement of fetal head circumference (HC)."""

    def __init__(self) -> None:
        """Initialize HC measurement."""
        super().__init__()

    def name(self) -> str:
        """Return the canonical name for this measurement."""
        return "head circumference"
