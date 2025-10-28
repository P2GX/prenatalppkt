"""
sonographic_measurement.py - Generic measurement mapper
"""

from typing import List
from prenatalppkt.measurements.term_bin import TermBin
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.term_observation import TermObservation


class SonographicMeasurement:
   """
   Generic measurement mapper using configured TermBins.
   
   This class replaces all measurement-specific subclasses.
   Configuration is injected via TermBins.
   """
   
   def __init__(self, measurement_type: str, term_bins: List[TermBin]):
       """
       Initialize with measurement type and HPO mappings.
       
       Args:
           measurement_type: e.g., "head_circumference"
           term_bins: Pre-configured list of TermBins from YAML
       """
       self.measurement_type = measurement_type
       self.term_bins = term_bins
   
   def from_percentile(
       self,
       percentile: float,
       gestational_age: GestationalAge
   ) -> TermObservation:
       """
       Map a percentile value to an HPO term observation.
       
       This is DATA-DRIVEN - no hardcoded if/elif chains!
       
       Args:
           percentile: Percentile value (0-100)
           gestational_age: Gestational age context
           
       Returns:
           TermObservation with appropriate HPO term
           
       Raises:
           ValueError: If no bin matches the percentile
       """
       # Iterate through bins to find matching one
       for term_bin in self.term_bins:
           if term_bin.fits(percentile):
               return TermObservation(
                   hpo_id=term_bin.hpo_id,
                   hpo_label=term_bin.hpo_label,
                   category=term_bin.category,
                   observed=not term_bin.normal,
                   gestational_age=gestational_age,
                   percentile=percentile
               )
       
       # No matching bin found
       raise ValueError(
           f"No HPO mapping found for {self.measurement_type} "
           f"percentile {percentile:.1f}"
       )
   
   def name(self) -> str:
       """Return the measurement type name."""
       return self.measurement_type