"""
src/prenatalppkt/dto/observer/builders/fetus_biometry_data.py

Biometric measurements, ratios, and estimated fetal weights grouping.
"""

from dataclasses import dataclass
from typing import Optional
from ..fetuses.measurements_data import MeasurementsData
from ..fetuses.ratios_data import FetusRatiosData
from ..fetuses.efw_data import FetusEfwData


@dataclass
class FetusBiometryData:
    """
    Grouped biometric data from Observer JSON.

    Attributes:
        measurements: Quantitative measurements (BPD, HC, AC, FL, etc.)
        ratios: Computed biometric ratios (HC/AC, FL/AC, FL/BPD)
        efws: Estimated fetal weight calculations
    """

    measurements: Optional[MeasurementsData] = None
    ratios: Optional[FetusRatiosData] = None
    efws: Optional[FetusEfwData] = None

    def __repr__(self) -> str:
        meas_count = self.measurements.measurement_count if self.measurements else 0
        ratio_count = self.ratios.ratio_count if self.ratios else 0
        efw_count = self.efws.efw_count if self.efws else 0

        return (
            f"FetusBiometryData("
            f"measurements={meas_count}, "
            f"ratios={ratio_count}, "
            f"efws={efw_count})"
        )
