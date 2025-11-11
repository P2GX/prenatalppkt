"""
src/prenatalppkt/dto/fetus/observer/fetus_environment_data.py

Fetal environment data grouping (fluids, vessels, placenta).
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class FetusEnvironmentData:
    """
    Grouped fetal environment data from Observer JSON.

    Attributes:
        amioticfluid: Amniotic fluid volume and AFI measurements
        fetalvessels: Umbilical artery/vein Doppler measurements
        placenta: Placenta position, grade, and characteristics
        uards: Ultrasound-adjusted risk for Down syndrome
    """

    amioticfluid: Optional[Any] = None
    fetalvessels: Optional[Any] = None
    placenta: Optional[Any] = None
    uards: Optional[Any] = None

    def __repr__(self) -> str:
        components_present = sum(
            [
                self.amioticfluid is not None,
                self.fetalvessels is not None,
                self.placenta is not None,
                self.uards is not None,
            ]
        )
        return f"FetusEnvironmentData(components_present={components_present})"
