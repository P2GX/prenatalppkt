"""
Abstract base class for biometry extractors.

Defines the contract that all concrete extractors must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
from prenatalppkt.etl.models.biometry import BiometryCollection
from prenatalppkt.etl.constants import (
    BiometryMeasurement,
    normalize_measurement_name,
    is_target_measurement,
)


class BiometryExtractor(ABC):
    """
    Abstract base class for extracting fetal biometry measurements.

    Subclasses must implement format-specific extraction logic for:
    - Observer JSON
    - ViewPoint text files
    - ViewPoint HL7 messages

    Target biometries (8 total):
    - HC (Head Circumference)
    - BPD (Biparietal Diameter)
    - AC (Abdominal Circumference)
    - Femur/FL (Femur Length)
    - Nuchal Fold
    - Cerebellum
    - OFD (Occipito-Frontal Diameter) - if present
    - Humerus/HL (Humerus Length) - if present
    """

    # Subclasses should set this to their format-specific name map
    FORMAT_NAME_MAP: Optional[Dict[str, BiometryMeasurement]] = None

    @abstractmethod
    def extract(self, data: Any) -> BiometryCollection:
        """
        Extract biometry measurements from input data.

        Args:
            data: Input data in format-specific structure
                  (dict for JSON, str for text, etc.)

        Returns:
            BiometryCollection with extracted measurements

        Raises:
            ValueError: If data is malformed or missing required fields
        """
        pass

    def extract_from_file(self, filepath: Path) -> BiometryCollection:
        """
        Extract biometry measurements from a file.

        Args:
            filepath: Path to input file

        Returns:
            BiometryCollection with extracted measurements
        """
        data = self._read_file(filepath)
        return self.extract(data)

    @abstractmethod
    def _read_file(self, filepath: Path) -> Any:
        """
        Read and parse file into appropriate data structure.

        Args:
            filepath: Path to input file

        Returns:
            Parsed data in format suitable for extract()
        """
        pass

    def _normalize_name(self, raw_name: str) -> str:
        """
        Normalize measurement name to standard form using format-specific mapping.

        Args:
            raw_name: Raw measurement name from input

        Returns:
            Standardized measurement name (from BiometryMeasurement enum)

        Raises:
            ValueError: If name cannot be normalized

        Example:
            TODO @VarenyaJ
        """
        return normalize_measurement_name(raw_name, self.FORMAT_NAME_MAP)

    def _is_target_measurement(self, raw_name: str) -> bool:
        """
        Check if a measurement name corresponds to a target biometry.

        Args:
            raw_name: Raw measurement name from input

        Returns:
            True if this is a target measurement, False otherwise
        """
        return is_target_measurement(raw_name, self.FORMAT_NAME_MAP)

    def _convert_to_mm(self, value: float, unit: str) -> float:
        """
        Convert measurement to millimeters.

        Args:
            value: Measurement value
            unit: Unit of measure (cm, mm)

        Returns:
            Value converted to millimeters

        Raises:
            ValueError: If unit is not supported
        """
        unit_lower = unit.lower().strip()

        if unit_lower in ["mm", "millimeters", "millimeter"]:
            return value
        elif unit_lower in ["cm", "centimeters", "centimeter"]:
            return value * 10.0
        else:
            raise ValueError(f"Unsupported unit: {unit}")

    def _parse_percentile(self, percentile_str: str) -> float:
        """
        Parse percentile string to float.

        Handles special cases:
        - "<1%" -> 0.5
        - ">99%" -> 99.5
        - "55%" -> 55.0
        - "55" -> 55.0

        Args:
            percentile_str: Percentile as string

        Returns:
            Percentile as float (0-100 scale)
        """
        if not percentile_str:
            return None

        s = str(percentile_str).strip()

        # Handle special cases
        if s.startswith("<"):
            # "<1%" -> treat as 0.5 (below 1st percentile)
            return 0.5
        elif s.startswith(">"):
            # ">99%" -> treat as 99.5 (above 99th percentile)
            return 99.5

        # Remove % sign if present
        s = s.rstrip("%")

        try:
            return float(s)
        except ValueError:
            raise ValueError(f"Could not parse percentile: {percentile_str}")
