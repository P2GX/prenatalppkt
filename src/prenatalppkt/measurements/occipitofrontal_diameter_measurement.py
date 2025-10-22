"""
occipitofrontal_diameter_measurement.py

Defines `OccipitofrontalDiameterMeasurement`, representing fetal abdominal
occipitofrontal diameter (OFD). Registered under `"occipitofrontal_diameter"`.
"""

from __future__ import annotations
from prenatalppkt.sonographic_measurement import SonographicMeasurement


class OccipitofrontalDiameterMeasurement(SonographicMeasurement, measurement_type="occipitofrontal_diameter"):
   """Represents a sonographic measurement of fetal occipitofrontal diameter (OFD)."""

    def __init__(self) -> None:
        """Initialize OFD measurement."""
        super().__init__()

   
   def name(self) -> str:
       """Return the canonical name for this measurement."""
       return "occipitofrontal diameter"
