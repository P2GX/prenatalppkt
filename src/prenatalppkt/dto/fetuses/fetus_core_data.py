"""
src/prenatalppkt/dto/fetuses/fetus_core_data.py
Core metadata for one fetus entry in the 'fetuses' array.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FetusCoreData:
   """
   Core fetal-level attributes extracted from the 'fetus' subkey.

   Attributes:
       fetus_number: Numeric identifier
       gender: Reported fetal sex
       ga_by_sonography: Gestational age (weeks) estimated by ultrasound
       heart_bpm: Heart rate in beats per minute
       heart_rate_is: Qualitative description (e.g., "Normal")
       fetus_growth: Growth descriptor (e.g., "Appropriate")
       fetus_presentation: Presentation position (e.g., "Vertex")
   """

   fetus_number: Optional[int] = None
   gender: Optional[str] = None
   ga_by_sonography: Optional[float] = None
   heart_bpm: Optional[int] = None
   heart_rate_is: Optional[str] = None
   fetus_growth: Optional[str] = None
   fetus_presentation: Optional[str] = None

   def __repr__(self) -> str:
       return (
           f"FetusCoreData("
           f"number={self.fetus_number}, gender={self.gender}, "
           f"GA={self.ga_by_sonography}, bpm={self.heart_bpm}, "
           f"presentation={self.fetus_presentation})"
       )