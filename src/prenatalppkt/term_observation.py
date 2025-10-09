"""
term_observation.py

Defines `TermObservation`, the ontology-aware representation of a fetal biometric measurement.

A `TermObservation` associates:
    - a `MeasurementResult` (percentile bin)
    - a corresponding ontology concept (`MinimalTerm` from hpotk)
    - and an observation status (observed / excluded)
for a given gestational age.

"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Set
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
    ) -> dict[str, Optional[MinimalTerm]]:
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
        *,
        normal_bins: Optional[Set[str]] = None,
        interpret_as_normal: bool = False,
    ) -> TermObservation:
        """
        Convert a MeasurementResult into a TermObservation using a bin->term mapping.

        The caller can specify what percentile bins count as "normal".

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
        normal_bins : Optional[set[str]]
            Optional set of percentile bin keys considered normal. If None, no bins are automatically excluded.
        interpret_as_normal : bool
            If True, treat this observation as explicitly normal (excluded) regardless of percentile bin (used for manual overrides).

        Returns
        -------
        TermObservation
        """
        bin_key = measurement_result.bin_key
        hpo_term = (bin_to_term or {}).get(bin_key)

        # Determine observed flag: caller decides what "normal" means
        if interpret_as_normal:
            observed = False
        elif normal_bins is not None:
            observed = bool(hpo_term and bin_key not in normal_bins)
        else:
            # If no normal_bins provided, assume all terms are observed
            observed = bool(hpo_term)

        return TermObservation(
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
