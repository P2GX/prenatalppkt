"""
src/prenatalppkt/dto/efw_data.py

Data Transfer Object for Estimated Fetal Weight (EFW) calculations. Each entry represents an EFW method (e.g., AC+FL+HC).
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EfwEntry:
   """Single EFW record for a given formula or measurement combination."""

   fetus_number: int
   label: str
   value: float
   decimal_places: int
   calculated_percentile: float
   percentile_for_display: str
   print_in_report: bool
   range_str: str


@dataclass
class FetusEfwData:
   """Collection of EFW entries for a fetus."""

   fetus_number: Optional[int]
   efw_entries: List[EfwEntry]

   @property
   def efw_count(self) -> int:
       """Number of EFW entries."""
       return len(self.efw_entries)

   def get_efw_by_label(self, label: str) -> Optional[EfwEntry]:
       """Retrieve an EFW entry by label (case-insensitive)."""
       for entry in self.efw_entries:
           if entry.label.lower() == label.lower():
               return entry
       return None