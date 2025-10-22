"""
term_observation.py

Defines the `TermObservation` class -- the ontology-aware interpretation of a
quantitative fetal sonographic measurement.

Overview
--------
This module bridges quantitative measurements (via `MeasurementResult`) with
ontology terms (via `MinimalTerm` from hpotk).  It provides a consistent way to
represent whether a given percentile-based result should be treated as an
*observed abnormality* or an *excluded normal finding* in downstream analysis.

Unlike earlier implementations, `TermObservation` does **not** assume any
specific definition of "normal."  Instead, the calling application (or study
configuration) must explicitly pass the set of percentile bins considered
normal.  This decouples numeric logic from clinical semantics and allows
population- or study-specific interpretations.

Responsibilities
----------------
1. **Mapping construction**
 - Provides `build_standard_bin_mapping()` to generate a canonical mapping
   between percentile bin keys (e.g., `"below_3p"`, `"between_90p_95p"`) and
   ontology terms (`MinimalTerm` objects).

2. **Observation derivation**
 - Converts a `MeasurementResult` into a `TermObservation` using
   `from_measurement_result()`.
 - The caller supplies both the mapping and the definition of what percentile
   bins are considered "normal".

3. **Serialization**
 - Exports an ontology-aware measurement as a simple dictionary conforming to
   Phenopacket JSON expectations via `to_phenotypic_feature()`.

Design Principles
-----------------
- **No hard-coded normal ranges.**  The logic for what is "normal" is
*injected* by the application, allowing different percentile thresholds for
different populations, studies, or biometric parameters.

- **Separation of concerns.**  Numeric percentile evaluation is handled by
`MeasurementResult`; semantic interpretation (normal vs abnormal phenotype)
lives here; and ontology term selection happens in higher-level mappings.

Example
-------
  from prenatalppkt.measurements.measurement_result import MeasurementResult
  from prenatalppkt.term_observation import TermObservation

  # Step 1: Define or load percentile bin mapping
  mapping = TermObservation.build_standard_bin_mapping(
      lower_extreme_term=microcephaly_term,
      lower_term=decreased_head_circumference_term,
      abnormal_term=abnormal_skull_term,
      normal_term=normal_skull_term,
      upper_term=increased_head_circumference_term,
      upper_extreme_term=macrocephaly_term,
  )

  # Step 2: Define what bins count as "normal" for this analysis
  normal_bins = {"between_10p_50p", "between_50p_90p"}

  # Step 3: Convert a MeasurementResult to a TermObservation
  result = reference_range.evaluate(value_mm)
  obs = TermObservation.from_measurement_result(
      measurement_result=result,
      bin_to_term=mapping,
      gestational_age=ga,
      normal_bins=normal_bins,
  )

  # Step 4: Serialize for Phenopacket export
  feature = obs.to_phenotypic_feature()

Notes
-----
- The `normal_bins` argument provides full configurability.  If omitted, all
bins with ontology terms are treated as "observed" (no normal range exclusion).
- The `interpret_as_normal` flag can explicitly mark an observation as normal,
even if percentile data are unavailable (e.g., clinician-reviewed cases).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Set
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
            # MinimalTerm stores the ID as 'identifier', not 'term_id'
            if hasattr(self.hpo_term, "identifier"):
                self.hpo_id = str(self.hpo_term.identifier)
            else:
                self.hpo_id = ""

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
        bin_to_term: dict,
        gestational_age: GestationalAge,
        *,
        normal_bins: Optional[Set[str]] = None,
        abnormal_term: Optional["MinimalTerm"] = None,
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

        Returns
        -------
        TermObservation
        """
        bin_key = measurement_result.bin_key
        hpo_term = bin_to_term.get(bin_key)

        if normal_bins and bin_key in normal_bins:
            # For normal bins -> use parent abnormal term, mark excluded
            hpo_term = abnormal_term
            observed = False
        else:
            observed = bool(hpo_term)

        return TermObservation(
            hpo_term=hpo_term, observed=observed, gestational_age=gestational_age
        )

    # ------------------------------------------------------------------ #
    # Serialization
    # ------------------------------------------------------------------ #
    # def to_phenotypic_feature(self) -> dict:
    #    """Serialize to a Phenopacket-style dictionary."""
    #    if self.hpo_term is None:
    #        return {"excluded": True, "description": "Measurement within normal range for gestational age", "description": f"Measurement within normal range for gestational age ({self.gestational_age.weeks}w{self.gestational_age.days}d)"}
    #    return {"type": {"id": self.hpo_id, "label": self.hpo_label}, "excluded": not self.observed, "description": f"Measurement at {self.gestational_age.weeks}w{self.gestational_age.days}d"}

    def to_phenotypic_feature(self) -> dict:
        """Serialize to a Phenopacket-style dictionary."""
        ga_str = f"{self.gestational_age.weeks}w{self.gestational_age.days}d"

        feature = {
            "excluded": not self.observed,
            "description": f"Measurement at {ga_str}",
        }

        # Always include a 'type' field, even if no HPO term is available
        if self.hpo_term:
            feature["type"] = {"id": self.hpo_id, "label": self.hpo_label}
        else:
            feature["type"] = {
                "id": "HP:0000118",
                "label": "Phenotypic abnormality (unspecified)",
            }
        # Always add normal-range text if excluded (normal finding)
        if not self.observed:
            feature["description"] = (
                f"Measurement within normal range for gestational age ({ga_str})"
            )

        return feature

    def __repr__(self) -> str:
        label = self.hpo_label or "None"
        return f"TermObservation(hpo_label='{label}', observed={self.observed}, ga={self.gestational_age.weeks}w{self.gestational_age.days}d)"
