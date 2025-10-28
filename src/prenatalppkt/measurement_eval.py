"""
term_observation.py - Simple data holder for HPO observations
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TermObservation:
   """
   HPO term observation with context.
   
   This is a DATA-ONLY class - no business logic.
   
   Attributes:
       hpo_id: HPO identifier (e.g., "HP:0000252")
       hpo_label: Human-readable label
       category: Category for provenance
       observed: True if abnormality observed, False if excluded
       gestational_age: Gestational age context
       percentile: Original percentile value (for provenance)
   """
   hpo_id: str
   hpo_label: str
   category: str
   observed: bool
   gestational_age: "GestationalAge"
   percentile: Optional[float] = None
   
   def __str__(self) -> str:
       status = "OBSERVED" if self.observed else "EXCLUDED"
       ga_str = f"{self.gestational_age.weeks}w{self.gestational_age.days}d"
       return f"{status}: {self.hpo_label} ({self.hpo_id}) at {ga_str}"