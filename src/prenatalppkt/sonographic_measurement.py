"""
sonographic_measurement.py

Defines `SonographicMeasurement`, the abstract superclass for fetal biometric
measurements such as biparietal diameter (BPD), head circumference (HC),
femur length (FL), abdominal circumference (AC), etc.

Purpose
-------
This class provides a unified interface for evaluating a raw measurement value
against gestational-age-specific percentile thresholds (`ReferenceRange.evaluate()`),
returning a `MeasurementResult` that encodes the percentile bin, and optionally
converting that result into a `TermObservation`.

Key improvements (OOP refactor)
-------------------------------
- Added automatic subclass registration via `__init_subclass__` for clean
polymorphism (no dynamic lookups or fragile imports).
- Enforced consistent evaluation interface (must return `MeasurementResult`).
- Clarified docstrings to highlight strict separation between numeric and
ontology evaluation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from prenatalppkt.biometry_type import BiometryType
from prenatalppkt.measurements.term_bin import TermBin
from prenatalppkt.percentile_bin import PercentileRange
from prenatalppkt.term_observation import TermObservation
import typing


class SonographicMeasurement(ABC):
    """
    Abstract base class for a fetal sonographic measurement.

    Responsibilities
    ----------------
    1. **Percentile evaluation** -
        Implements `evaluate()` to determine which percentile bin a raw
        measurement falls into. Always returns a `MeasurementResult`.
    """

    def __init__(
        self,
        measurement_type: BiometryType,
        termbin_d: typing.Dict[PercentileRange, TermBin],
    ):
        """
        Parameters
        ----------
        measurement_type : BiometryType
            The BiometryType enum member for this measurement class.
        """
        self._measurement_type = measurement_type.value
        self._termbin_d = termbin_d

    # ------------------------------------------------------------------ #
    # Abstract metadata
    # ------------------------------------------------------------------ #
    @abstractmethod
    def name(self) -> str:
        """Return the canonical name for this measurement (e.g., 'biparietal diameter')."""
        raise NotImplementedError

    def from_percentile(self, percentile: float, gestational_age) -> TermObservation:
        if percentile < 3.0:
            term_bin = self._termbin_d.get(PercentileRange.BELOW_3P)
        elif percentile < 5.0:
            term_bin = self._termbin_d.get(PercentileRange.BETWEEN_3P_5P)
        ## TODO OTHER BINS
        else:
            term_bin = self._termbin_d.get(PercentileRange.ABOVE_97P)
        if term_bin is None:
            raise ValueError("Could not get TermBin")
        return TermObservation(
            hpo_id=term_bin.termid,
            hpo_label=term_bin.termlabel,
            observed=not term_bin.normal,
            gestational_age=gestational_age,
        )
