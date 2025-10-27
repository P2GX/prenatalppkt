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
    hpo_id: str
    hpo_label: str
    observed: bool
    gestational_age: GestationalAge
   
    
    


    