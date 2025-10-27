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
from typing import Optional, Dict, ClassVar
from hpotk import MinimalTerm
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.measurement_result import MeasurementResult
from prenatalppkt.term_observation import TermObservation


class SonographicMeasurement(ABC):
    """
    Abstract base class for a fetal sonographic measurement.

    Responsibilities
    ----------------
    1. **Percentile evaluation** -
        Implements `evaluate()` to determine which percentile bin a raw
        measurement falls into. Always returns a `MeasurementResult`.

    2. **Subclass registry** -
        Subclasses register automatically under a canonical name (e.g.
        "head_circumference"), allowing lookup by exporters or other tools
        without fragile import-time maps.

    3. **Optional ontology mapping** -
        The `to_term_observation()` convenience method can convert a
        MeasurementResult into a TermObservation, but the canonical
        ontology mapping happens downstream.
    """

    # ------------------------------------------------------------------ #
    # Automatic registry for subclasses
    # ------------------------------------------------------------------ #
    registry: ClassVar[dict[str, type["SonographicMeasurement"]]] = {}

    def __init_subclass__(cls, measurement_type: Optional[str] = None, **kwargs):
        """
        Automatically register subclasses in the measurement registry.

        If `measurement_type` is not explicitly provided, it defaults to the lowercase class name with 'Measurement' stripped (e.g., 'BiparietalDiameterMeasurement' -> 'biparietaldiameter').
        """
        super().__init_subclass__(**kwargs)
        key = measurement_type or cls.__name__.replace("Measurement", "").lower()
        cls.registry[key] = cls

    # ------------------------------------------------------------------ #
    # Abstract metadata
    # ------------------------------------------------------------------ #
    @abstractmethod
    def name(self) -> str:
        """Return the canonical name for this measurement (e.g., 'biparietal diameter')."""
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Core evaluation
    # ------------------------------------------------------------------ #
    def evaluate(
        self, gestational_age: GestationalAge, measurement_value: float, reference_range
    ) -> MeasurementResult:
        """
        Evaluate a raw measurement against the provided reference range.

        Returns
        -------
        MeasurementResult
            Encodes which percentile interval the value falls into.

        Notes
        -----
        Subclasses should not override this unless they need special handling.
        Ontology mapping happens in TermObservation or the exporter layer.
        """
        return reference_range.evaluate(measurement_value)

    # ------------------------------------------------------------------ #
    # Convenience ontology conversion
    # ------------------------------------------------------------------ #
    def to_term_observation(
        self,
        measurement_result: MeasurementResult,
        gestational_age: GestationalAge,
        parent_term: Optional[MinimalTerm] = None,
    ) -> TermObservation:
        """
        Convert a MeasurementResult into a minimal TermObservation
        (mainly for debugging or basic interoperability).

        Parameters
        ----------
        measurement_result : MeasurementResult
            The evaluated percentile bin.
        gestational_age : GestationalAge
            Gestational context.
        parent_term : Optional[MinimalTerm]
            The anatomical/measurement-level ontology term (e.g. "Abnormality of skull size").
        """
        observed = measurement_result.bin_key not in {
            "between_10p_50p",
            "between_50p_90p",
        }
        return TermObservation(
            hpo_term=parent_term, observed=observed, gestational_age=gestational_age
        )

    def get_bin_to_term_mapping(self) -> Dict[str, Optional[MinimalTerm]]:
        """
        Optional default bin->term mapping (usually overridden or configured externally).
        """
        return TermObservation.build_standard_bin_mapping(
            lower_extreme_term=None,
            lower_term=None,
            abnormal_term=None,
            normal_term=None,
            upper_term=None,
            upper_extreme_term=None,
        )
