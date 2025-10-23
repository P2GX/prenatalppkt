"""
term_observation.py

Defines `TermObservation`, the ontology-aware interpretation of a
quantitative fetal sonographic measurement.

This version is fully aligned with the refactored exporter:
- Always used as the final semantic representation (not mixed with raw results).
- Clarified docstrings on its relationship to `PhenotypicExporter.evaluate_to_observation`.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Set
import typing
from hpotk import MinimalTerm
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.measurement_result import MeasurementResult


@dataclass
class TermObservation:
    """
    Represents an ontology-based interpretation of a MeasurementResult.

    Attributes
    ----------
    hpo_term : Optional[MinimalTerm]
        The ontology term representing the phenotype (e.g., "Microcephaly").
    observed : bool
        True if abnormality observed; False if excluded (normal finding).
    gestational_age : GestationalAge
        Context for interpretation.
    """

    hpo_term: Optional[MinimalTerm]
    observed: bool
    gestational_age: GestationalAge
    parent_term: Optional[MinimalTerm] = None
    hpo_id: str = ""
    hpo_label: str = ""

    def __post_init__(self) -> None:
        """Derive identifiers and labels from MinimalTerm."""
        if self.hpo_term and isinstance(self.hpo_term, MinimalTerm):
            self.hpo_id = str(getattr(self.hpo_term, "identifier", ""))
            self.hpo_label = getattr(self.hpo_term, "name", "")

    # ------------------------------------------------------------------ #
    # Mapping utilities
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
    ) -> dict[str, Optional[MinimalTerm]]:
        """Return canonical percentile-bin-to-term mapping."""
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
    # Factory constructor
    # ------------------------------------------------------------------ #
    @classmethod
    def from_measurement_result(
        cls,
        measurement_result: MeasurementResult,
        bin_to_term: dict,
        gestational_age: GestationalAge,
        *,
        normal_bins: Optional[Set[str]] = None,
        abnormal_term: Optional["MinimalTerm"] = None,
    ) -> TermObservation:
        """
        Convert a MeasurementResult into a TermObservation using a bin->term mapping.
        """
        bin_key = measurement_result.bin_key
        hpo_term = bin_to_term.get(bin_key)

        if normal_bins and bin_key in normal_bins:
            # For normal bins -> use parent abnormal term, mark excluded
            hpo_term = abnormal_term
            observed = False
        elif hpo_term is None:
            # For abnormal bins with no specific term -> use abnormal_term as fallback
            hpo_term = abnormal_term
            observed = True
        else:
            # Have a specific term for this bin
            observed = True

        return TermObservation(
            hpo_term=hpo_term, observed=observed, gestational_age=gestational_age
        )

    # ------------------------------------------------------------------ #
    # Serialization
    # ------------------------------------------------------------------ #
    def to_phenotypic_feature(self) -> typing.Dict[str, str]:
        """Serialize to Phenopacket-compatible dictionary."""
        ga_str = f"{self.gestational_age.weeks}w{self.gestational_age.days}d"
        feature = {
            "excluded": not self.observed,
            "description": f"Measurement at {ga_str}",
        }
        if self.hpo_term:
            feature["type"] = {"id": self.hpo_id, "label": self.hpo_label}
        else:
            feature["type"] = {
                "id": "HP:0000118",
                "label": "Phenotypic abnormality (unspecified)",
            }
        if not self.observed:
            feature["description"] = (
                f"Measurement within normal range for gestational age ({ga_str})"
            )
        return feature

    def __repr__(self) -> str:
        label = self.hpo_label or "None"
        return f"TermObservation(hpo_label='{label}', observed={self.observed}, ga={self.gestational_age.weeks}w{self.gestational_age.days}d)"
