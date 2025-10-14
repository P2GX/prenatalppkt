"""
femur_length_measurement.py

Defines `FemurLengthMeasurement`, a subclass of `SonographicMeasurement`
for fetal femur length (FL) evaluation.

This class provides a consistent interface for percentile evaluation
without embedding any reference data directly.  Actual reference tables
will be injected via parsing utilities in a future PR.
"""

from __future__ import annotations

from hpotk import MinimalTerm
from prenatalppkt.sonographic_measurement import SonographicMeasurement


HPO_SHORT_FEMUR = "HP:0011428"  # Short fetal femur length
HPO_LONG_FEMUR = "HP:9999999"  # Placeholder - if HPO doesn't define it, keep as custom
HPO_ABN_FEMUR = "HP:9999999"  # Placeholder - if HPO doesn't define it, keep as custom

short_femur = MinimalTerm.create_minimal_term(term_id= "HP:0011428", name="Short fetal femur length", alt_term_ids=[], is_obsolete=False)
long_femur = MinimalTerm.create_minimal_term(term_id= "HP:9999999", name="Long fetal femur length", alt_term_ids=[], is_obsolete=False)
abn_femur = MinimalTerm.create_minimal_term(term_id= "HP:9999999", name="Abnormal fetal femur length", alt_term_ids=[], is_obsolete=False)

class FemurLengthMeasurement(SonographicMeasurement):
    """
    Represents a sonographic measurement of fetal femur length (FL).

    Responsibilities
    ----------------
    - Provides a canonical measurement name.
    - Defines a placeholder for ontology mapping.
    - Delegates percentile evaluation logic to the superclass.
    """

    def __init__(self) -> None:
        """Initialize femur length measurement."""
        super().__init__(low=short_femur, abn=abn_femur, high=long_femur)

    def name(self) -> str:
        """Return the canonical name for this measurement."""
        return "femur length"
