"""
head_circumference_measurement.py

Defines `HeadCircumferenceMeasurement`, a subclass of `SonographicMeasurement`
for fetal head circumference (HC) evaluation.

Automatically registered under `"head_circumference"`.
"""

from __future__ import annotations
import typing
from prenatalppkt.measurements.term_bin import TermBin
from prenatalppkt.percentile_bin import PercentileRange
from prenatalppkt.sonographic_measurement import SonographicMeasurement
from prenatalppkt.biometry_type import BiometryType


class HeadCircumferenceMeasurement(SonographicMeasurement):
    """Represents a sonographic measurement of fetal head circumference (HC)."""

    def __init__(self, termbin_d: typing.Dict[PercentileRange, TermBin]) -> None:
        """Initialize HC measurement."""
        super().__init__(
            measurement_type=BiometryType.HEAD_CIRCUMFERENCE, termbin_d=termbin_d
        )

    def name(self) -> str:
        """Return the canonical name for this measurement."""
        return "head circumference"
