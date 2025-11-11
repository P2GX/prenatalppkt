"""
src/prenatalppkt/dto/fetus/observer/fetus_gestational_data.py

Early pregnancy and gestational data grouping.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class FetusGestationalData:
    """
    Grouped early pregnancy data from Observer JSON.

    Attributes:
        firsttrimester: First trimester findings (yolk sac, fetal pole, etc.)
        ectopic_preg: Ectopic pregnancy assessment data
    """

    firsttrimester: Optional[Any] = None
    ectopic_preg: Optional[Any] = None

    def __repr__(self) -> str:
        return (
            f"FetusGestationalData("
            f"firsttrimester={'present' if self.firsttrimester else 'absent'}, "
            f"ectopic_preg={'present' if self.ectopic_preg else 'absent'})"
        )
