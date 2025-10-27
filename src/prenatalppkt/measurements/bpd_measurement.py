"""
bpd_measurement.py

Defines `BiparietalDiameterMeasurement`, a subclass of `SonographicMeasurement`
for fetal biparietal diameter (BPD) evaluation.

This class implements the structural hooks for gestational-age-specific
evaluation and ontology mapping but does not hardcode reference data.
Percentile thresholds will be dynamically loaded in a future PR via the
percentile parsing pipeline (NIHCD/INTERGROWTH tables).
"""

from __future__ import annotations
from prenatalppkt.sonographic_measurement import SonographicMeasurement


class BiparietalDiameterMeasurement(
    SonographicMeasurement, measurement_type="biparietal_diameter"
):
    """
    Represents a sonographic measurement of fetal biparietal diameter (BPD).

    Responsibilities
    ----------------
    - Provides a canonical measurement name.
    - Defines default ontology term mappings (if available).
    - Delegates percentile evaluation logic to the superclass.

    Reference Data
    --------------
    Reference ranges will be populated in a later PR that parses NIHCD and
    INTERGROWTH-21st tables for BPD percentile values.
    """

    def __init__(self) -> None:
        """Initialize BPD measurement."""
        super().__init__()

    def name(self) -> str:
        """Return the canonical name for this measurement."""
        return "biparietal diameter"
