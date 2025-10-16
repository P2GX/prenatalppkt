"""
sonographic_measurement.py

Defines `SonographicMeasurement`, the abstract superclass for fetal biometric
measurements such as biparietal diameter (BPD), head circumference (HC),
femur length (FL), abdominal circumference (AC), etc.

Purpose
-------
This class provides a unified interface for evaluating a raw measurement value
against gestational-age-specific percentile thresholds (`ReferenceRange.evaluate()`),
returning a `MeasurementResult` object that encodes the percentile bin, and optionally
converting that result into a `TermObservation` that maps the bin to ontology terms.

Unlike earlier versions, `SonographicMeasurement` itself no longer stores or configures
ontology mappings. Ontology mapping has been relocated to `TermObservation` to ensure
clean separation of concerns and testability. The class therefore only returns a
structural TermObservation indicating whether a measurement is within or outside the
expected range.

Usage
-----
A typical evaluation workflow looks like this:

  # Step 1: Compute the percentile bin
  result = bpd.evaluate(ga, 155.0, reference_range)

  # Step 2-5: Convert the bin to a TermObservation
  mapping = TermObservation.build_standard_bin_mapping(
      lower_extreme_term=microcephaly,
      lower_term=decreased_head_circumference,
      abnormal_term=abnormal_skull_size,
      normal_term=normal_skull_morphology,
      upper_term=increased_head_circumference,
      upper_extreme_term=macrocephaly,
  )
  obs = bpd.to_term_observation(result, ga, parent_term=skull_measurement)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict
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
        Calls `ReferenceRange.evaluate(value)` to determine which percentile bin
        a raw measurement falls into, returning a `MeasurementResult`.

    2. **Delegated ontology mapping** -
        Provides the convenience wrapper `to_term_observation()` which translates
        a `MeasurementResult` into a `TermObservation` using the subclass's bin->term mapping.

    3. **Subclass extensibility** -
        Each subclass (e.g., `BiparietalDiameterMeasurement`) overrides
        `get_bin_to_term_mapping()` or defines measurement-specific metadata.

    By decoupling evaluation from ontology mapping, this design preserves clean
    separation of logic (numeric evaluation vs semantic interpretation).
    """

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
        This method intentionally returns a `MeasurementResult` rather than a
        `TermObservation`. Ontology mapping (bin -> HPO term) is performed later
        by the exporter or by `to_term_observation()`.

        Subclasses may override this method to return a `TermObservation`
        directly if they wish to encapsulate both steps, but the exporter
        will handle either type safely.
        """
        return reference_range.evaluate(measurement_value)

        # NOTE(@VarenyaJ): Evaluation remains numeric-only for now.
        # Mapping to ontology happens downstream (TermObservation).

    # ------------------------------------------------------------------ #
    # Structural TermObservation
    # ------------------------------------------------------------------ #
    def to_term_observation(
        self,
        measurement_result: MeasurementResult,
        gestational_age: GestationalAge,
        parent_term: Optional[MinimalTerm] = None,
    ) -> TermObservation:
        """
        Convert a MeasurementResult into a TermObservation.

        This helps us later perform Steps 2-5 of the classic evaluation workflow:

            Step 2 - Resolve percentile bin -> ontology term using mapping
            Step 3 - Handle missing or normal bins (mark as unobserved)
            Step 4 - Determine observed flag (exclude 10th-90th)
            Step 5 - Return standardized TermObservation

        Parameters
        ----------
        measurement_result : MeasurementResult
            The evaluated percentile bin.
        gestational_age : GestationalAge
            Gestational context.
        parent_term : Optional[MinimalTerm]
            The anatomical/measurement-level ontology term
            (e.g. "Abnormality of skull size").

        Returns
        -------
        TermObservation
            A minimal observation object with observed/excluded status.
        """
        # Observed = True for abnormal bins (outside 10th-90th percentile)
        observed = measurement_result.bin_key not in {
            "between_10p_50p",
            "between_50p_90p",
        }
        return TermObservation(
            hpo_term=parent_term, observed=observed, gestational_age=gestational_age
        )

    def get_bin_to_term_mapping(self) -> Dict[str, Optional[MinimalTerm]]:
        """
        Placeholder for a default mapping of percentile bins to ontology terms.

        This lives in the superclass so all measurement subclasses share the
        same baseline structure. Each subclass may override this in a later
        ontology integration phase.
        """
        return TermObservation.build_standard_bin_mapping(
            lower_extreme_term=None,
            lower_term=None,
            abnormal_term=None,
            normal_term=None,
            upper_term=None,
            upper_extreme_term=None,
        )
