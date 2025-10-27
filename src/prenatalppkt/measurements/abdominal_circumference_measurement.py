"""
abdominal_circumference_measurement.py

Defines `AbdominalCircumferenceMeasurement`, representing fetal abdominal
circumference (AC). Automatically registered under `"abdominal_circumference"`.
"""

from __future__ import annotations
from prenatalppkt.sonographic_measurement import SonographicMeasurement
from prenatalppkt.biometry_type import BiometryType


class AbdominalCircumferenceMeasurement(
    SonographicMeasurement, measurement_type=BiometryType.ABDOMINAL_CIRCUMFERENCE
):
    """Represents a fetal abdominal circumference (AC) measurement."""

    def __init__(self) -> None:
        """Initialize BPD measurement."""
        super().__init__()

    def name(self) -> str:
        """Return the canonical name for this measurement."""
        return "abdominal circumference"
