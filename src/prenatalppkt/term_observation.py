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
    """
    _hpo_term: MinimalTerm
    _observed: bool
    _gestational_age: GestationalAge

   

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
            _hpo_term=hpo_term,
            _observed=observed,
            _gestational_age=gestational_age,
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

    
    @property
    def hpo_term(self) -> Optional["MinimalTerm"]:
        """The ontology term representing the phenotype."""
        return self._hpo_term

    @property
    def observed(self) -> bool:
        """True if the abnormality was observed; False if explicitly not observed."""
        return self._observed

    @property
    def gestational_age(self) -> "GestationalAge":
        """Gestational age context for the measurement."""
        return self._gestational_age

    # --- Derived convenience properties ---
    @property
    def hpo_id(self) -> Optional[str]:
        """Return the HPO term ID, if available."""
        return self._hpo_term.identifier.value if self._hpo_term else None

    @property
    def hpo_label(self) -> Optional[str]:
        """Return the HPO term label, if available."""
        return self._hpo_term.name if self._hpo_term else None
    
    def __repr__(self) -> str:
        label = self.hpo_label or "None"
        return f"TermObservation(hpo_label='{label}', observed={self.observed}, ga={self.gestational_age.weeks}w{self.gestational_age.days}d)"
