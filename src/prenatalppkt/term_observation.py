"""
term_observation.py

Defines `TermObservation`, the ontology-aware representation of a fetal biometric measurement.

A `TermObservation` associates:
    - a `MeasurementResult` (percentile bin)
    - a corresponding ontology concept (`MinimalTerm` from hpotk)
    - and an observation status (observed / excluded)
for a given gestational age.

This module centralizes the mapping between percentile bins and ontology terms. The mapping is configured through the `build_standard_bin_mapping()` helper, which implements the conventional six-term configuration pattern:

    lower_extreme_term : MinimalTerm
        Term for <3rd percentile (severe low extreme).
    lower_term : MinimalTerm
        Term for 3rd-5th percentile (mild low finding).
    abnormal_term : MinimalTerm
        Term for 5th-10th and 90th-95th percentiles (abnormal zone).
    normal_term : Optional[MinimalTerm]
        Optional term for 10th-90th percentile range (normal finding).
    upper_term : MinimalTerm
        Term for 95th-97th percentile (mild high finding).
    upper_extreme_term : MinimalTerm
        Term for >97th percentile (severe high extreme).

Example
-------
    >>> mapping = TermObservation.build_standard_bin_mapping(
    ...     lower_extreme_term=microcephaly,
    ...     lower_term=decreased_head_circumference,
    ...     abnormal_term=abnormal_skull_size,
    ...     normal_term=normal_skull_morphology,
    ...     upper_term=increased_head_circumference,
    ...     upper_extreme_term=macrocephaly,
    ... )
    >>> result = reference_range.evaluate(155.0)
    >>> obs = TermObservation.from_measurement_result(result, mapping, ga)

This corresponds exactly to the five logical steps that used to be embedded inside `SonographicMeasurement.evaluate()`:

    Step 1 - Compute percentile bin via `reference_range.evaluate(value)`
    Step 2 - Resolve bin -> term mapping
    Step 3 - Handle normal / unconfigured bins (no HPO term => unobserved)
    Step 4 - Determine observed flag (exclude 10th-90th)
    Step 5 - Return standardized TermObservation
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
from hpotk import MinimalTerm
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.measurement_result import MeasurementResult

# Canonical normal bins used for exclusion logic
_NORMAL_BINS = {"between_10p_50p", "between_50p_90p"}


@dataclass
class TermObservation:
    """
    Represents an ontology-based interpretation of a MeasurementResult.

    Attributes
    ----------
    hpo_term : Optional[MinimalTerm]
        The ontology term representing the phenotype (e.g., "Microcephaly").
    observed : bool
        True if the abnormality was observed; False if explicitly not observed (normal finding / excluded).
    gestational_age : GestationalAge
        Gestational age context for the measurement.
    parent_term : Optional[MinimalTerm]
        Optional ontology parent term used for grouping or hierarchical context.
    hpo_id, hpo_label : str
        Convenience accessors automatically populated from `hpo_term`.
    """

    hpo_term: Optional[MinimalTerm]
    observed: bool
    gestational_age: GestationalAge
    parent_term: Optional[MinimalTerm] = None
    hpo_id: str = ""
    hpo_label: str = ""

    def __post_init__(self) -> None:
        """Populate identifier and label from MinimalTerm when available."""
        if self.hpo_term and isinstance(self.hpo_term, MinimalTerm):
            self.hpo_id = getattr(self.hpo_term, "term_id", "")
            self.hpo_label = getattr(self.hpo_term, "name", "")

    # ------------------------------------------------------------------ #
    # Mapping Builders
    # ------------------------------------------------------------------ #
    @staticmethod
    def build_standard_bin_mapping(
        *,
        lower_extreme_term: MinimalTerm,
        lower_term: MinimalTerm,
        abnormal_term: MinimalTerm,
        normal_term: Optional[MinimalTerm] = None,
        upper_term: MinimalTerm,
        upper_extreme_term: MinimalTerm,
    ) -> dict[str, MinimalTerm]:
        """
        Construct a canonical mapping from percentile bins to ontology terms.

        Each key corresponds to a percentile interval defined by `MeasurementResult`. Values are `MinimalTerm` objects.

        Returns
        -------
        dict[str, MinimalTerm]
            Complete mapping ready for use in `from_measurement_result()`.
        """
        return {
            "below_3p": lower_extreme_term,
            "between_3p_5p": lower_term,
            "between_5p_10p": abnormal_term,
            "between_10p_50p": normal_term,
            "between_50p_90p": normal_term,
            "between_90p_95p": abnormal_term,
            "between_95p_97p": upper_term,
            "above_97p": upper_extreme_term,
        }

    # ------------------------------------------------------------------ #
    # Factory Constructor
    # ------------------------------------------------------------------ #
    @classmethod
    def from_measurement_result(
        cls,
        measurement_result: MeasurementResult,
        bin_to_term: Optional[Dict[str, Optional[MinimalTerm]]],
        gestational_age: GestationalAge,
        parent_term: Optional[MinimalTerm] = None,
    ) -> TermObservation:
        """
        Convert a MeasurementResult into a TermObservation using a bin->term mapping.

        This method performs the complete five-step evaluation pipeline:

        Step 1 - Receives the `MeasurementResult` produced by `ReferenceRange.evaluate(value)`.
        Step 2 - Extracts the canonical bin key (`MeasurementResult.get_bin_key`).
        Step 3 - Looks up the corresponding ontology term in `bin_to_term`. If missing or None, the term is treated as "normal" (excluded).
        Step 4 - Determines the `observed` flag.  Bins between 10th and 90th percentiles are considered unobserved (normal) even if a nominal term is provided.
        Step 5 - Constructs and returns a `TermObservation` object ready for downstream Phenopacket export.

        Parameters
        ----------
        measurement_result : MeasurementResult
            The evaluated percentile bin.
        bin_to_term : dict[str, MinimalTerm] | None
            Mapping of percentile bins to ontology terms, typically produced by `build_standard_bin_mapping()`.
        gestational_age : GestationalAge
            Contextual gestational age of the measurement.
        parent_term : Optional[MinimalTerm]
            Optional ontology ancestor for grouping.

        Returns
        -------
        TermObservation
        """
        bin_key = measurement_result.get_bin_key
        hpo_term = bin_to_term.get(bin_key) if bin_to_term else None
        observed = bool(hpo_term and bin_key not in _NORMAL_BINS)
        return cls(
            hpo_term=hpo_term,
            observed=observed,
            gestational_age=gestational_age,
            parent_term=parent_term,
        )

    # ------------------------------------------------------------------ #
    # Serialization
    # ------------------------------------------------------------------ #
    def to_phenotypic_feature(self) -> dict:
        """Serialize to a Phenopacket-style dictionary."""
        if self.hpo_term is None:
            return {
                "excluded": True,
                "description": "Measurement within normal range for gestational age",
            }
        return {
            "type": {"id": self.hpo_id, "label": self.hpo_label},
            "excluded": not self.observed,
            "description": f"Measurement at {self.gestational_age.weeks}w{self.gestational_age.days}d",
        }

    def __repr__(self) -> str:
        label = self.hpo_label or "None"
        return f"TermObservation(hpo_label='{label}', observed={self.observed}, ga={self.gestational_age.weeks}w{self.gestational_age.days}d)"
