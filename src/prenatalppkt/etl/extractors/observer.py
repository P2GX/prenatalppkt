"""
Observer JSON biometry extractor.

Extracts fetal biometry measurements from Observer ultrasound system JSON exports.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from prenatalppkt.etl.extractors.base import BiometryExtractor
from prenatalppkt.etl.models.biometry import Biometry, BiometryCollection
from prenatalppkt.etl.constants import OBSERVER_NAME_MAP, BiometryMeasurement

logger = logging.getLogger(__name__)

# ruff: noqa: PERF203


class ObserverExtractor(BiometryExtractor):
    """
    Extract biometry measurements from Observer JSON format.

    Observer JSON structure:
        {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 25.0,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 42.5,
                            "calculated_ega": 27.1,
                            ...
                        },
                        ...
                    ]
                }
            ]
        }
    """

    # Use Observer-specific name mapping
    FORMAT_NAME_MAP = OBSERVER_NAME_MAP

    # Target measurements (canonical names)
    TARGET_LABELS = BiometryMeasurement.all_values()

    def extract(self, data: Dict[str, Any]) -> BiometryCollection:
        """
        Extract biometry measurements from Observer JSON.

        Args:
            data: Parsed Observer JSON dictionary

        Returns:
            BiometryCollection with extracted measurements

        Raises:
            ValueError: If JSON structure is invalid
        """
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict, got {type(data)}")

        if "fetuses" not in data:
            raise ValueError("Missing 'fetuses' key in Observer JSON")

        fetuses = data["fetuses"]
        if not fetuses or not isinstance(fetuses, list):
            raise ValueError("'fetuses' must be non-empty list")

        # Extract from first fetus (for now - can extend to handle multiple)
        fetus_data = fetuses[0]
        fetus_number = self._get_fetus_number(fetus_data)

        measurements = self._extract_measurements(fetus_data, fetus_number)

        logger.info(
            f"Extracted {len(measurements)} biometries from Observer JSON "
            f"(fetus {fetus_number})"
        )

        return BiometryCollection(measurements=measurements, fetus_number=fetus_number)

    def _read_file(self, filepath: Path) -> Dict[str, Any]:
        """Read Observer JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_fetus_number(self, fetus_data: Dict[str, Any]) -> Optional[int]:
        """Extract fetus number from fetus data."""
        fetus_section = fetus_data.get("fetus", {})
        return fetus_section.get("fetus_number")

    def _extract_measurements(
        self, fetus_data: Dict[str, Any], fetus_number: Optional[int]
    ) -> List[Biometry]:
        """
        Extract individual biometry measurements.

        Args:
            fetus_data: Single fetus dictionary from Observer JSON
            fetus_number: Fetus identifier

        Returns:
            List of Biometry objects
        """
        if "measurements" not in fetus_data:
            logger.warning("No 'measurements' key found in fetus data")
            return []

        measurements_list = fetus_data["measurements"]
        if not isinstance(measurements_list, list):
            raise ValueError("'measurements' must be a list")

        biometries = []

        for m in measurements_list:
            try:
                biometry = self._parse_measurement(m, fetus_number)
                if biometry:
                    biometries.append(biometry)
            except Exception as e:
                logger.warning(
                    f"Failed to parse measurement {m.get('label', 'unknown')}: {e}"
                )

        return biometries

    def _parse_measurement(
        self, m: Dict[str, Any], fetus_number: Optional[int]
    ) -> Optional[Biometry]:
        """
        Parse a single measurement dictionary into Biometry object.

        Args:
            m: Measurement dictionary
            fetus_number: Fetus identifier

        Returns:
            Biometry object or None if measurement not in target list
        """
        label = m.get("label")
        if not label:
            return None

        # Check if this is a target measurement
        if not self._is_target_measurement(label):
            return None

        # Normalize the label
        normalized_label = self._normalize_name(label)

        # Extract required fields
        value = m.get("value")
        if value is None:
            logger.debug(f"Skipping {label}: no value")
            return None

        unit = m.get("unit_of_measure", "cm")
        value_mm = self._convert_to_mm(float(value), unit)

        # Extract optional fields
        percentile = m.get("calculated_percentile")
        ega = m.get("calculated_ega")

        # Format gestational age if present
        gestational_age = None
        if ega is not None:
            gestational_age = self._format_gestational_age(ega)

        return Biometry(
            name=normalized_label,
            value_mm=value_mm,
            percentile=float(percentile) if percentile is not None else None,
            gestational_age=gestational_age,
            method=None,  # Observer JSON doesn't include method
            fetus_number=fetus_number,
        )

    def _format_gestational_age(self, ega: float) -> str:
        """
        Convert EGA in weeks to GA string format.

        Args:
            ega: Estimated gestational age in weeks (e.g., 27.1)

        Returns:
            Formatted string (e.g., "G27w0d")
        """
        weeks = int(ega)
        days = int((ega - weeks) * 7)
        return f"G{weeks}w{days}d"
