"""
src/prenatalppkt/dto/fetus/observer/fetus_procedures_data.py

Prenatal procedures and assessments grouping.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class FetusProceduresData:
    """
    Grouped prenatal procedures data from Observer JSON.

    Attributes:
        amniocentesis: Amniocentesis procedure details and results
        fbscvs: Fetal blood sampling and CVS (chorionic villus sampling)
        bpp: Biophysical profile scoring
        nst: Non-stress test results
        otherprocs: Other procedures performed
    """

    amniocentesis: Optional[Any] = None
    fbscvs: Optional[Any] = None
    bpp: Optional[Any] = None
    nst: Optional[Any] = None
    otherprocs: Optional[Any] = None

    def __repr__(self) -> str:
        procedures_present = sum(
            [
                self.amniocentesis is not None,
                self.fbscvs is not None,
                self.bpp is not None,
                self.nst is not None,
                self.otherprocs is not None,
            ]
        )
        return f"FetusProceduresData(procedures_present={procedures_present})"
