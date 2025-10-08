"""
femur_length_measurement.py

Defines `FemurLengthMeasurement`, a subclass of `SonographicMeasurement`
for fetal femur length (FL) evaluation.

This class provides a consistent interface for percentile evaluation
without embedding any reference data directly.  Actual reference tables
will be injected via parsing utilities in a future PR.
"""

from __future__ import annotations
from typing import Optional, Dict
from hpotk import MinimalTerm
from prenatalppkt.sonographic_measurement import SonographicMeasurement
from prenatalppkt.term_observation import TermObservation


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
        super().__init__()

    def name(self) -> str:
        """Return the canonical name for this measurement."""
        return "femur length"

    def get_bin_to_term_mapping(self) -> Dict[str, Optional[MinimalTerm]]:
        """
        Placeholder ontology mapping for femur length deviations.
        Future versions will attach skeletal growth-related HPO terms.
        """
        return TermObservation.build_standard_bin_mapping(
            lower_extreme_term=None,
            lower_term=None,
            abnormal_term=None,
            normal_term=None,
            upper_term=None,
            upper_extreme_term=None,
        )
