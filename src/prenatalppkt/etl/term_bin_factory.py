"""
TermBin factory for creating TermBin objects from raw biometry measurements.

This module provides a factory class that:
1. Loads HPO mappings once at initialization
2. Creates TermBin objects using existing infrastructure
3. Validates required measurements (HC, BPD, AC, Femur)
4. Handles optional measurements gracefully

Usage:
   factory = TermBinFactory()
   term_bin = factory.create_term_bin(
       name="HC",
       value_mm=250.0,
       percentile=42.5,
       gestational_age=GestationalAge(weeks=27, days=1),
       method="Hadlock",
       fetus_number=1
   )
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.mapping_loader import BiometryMappingLoader
from prenatalppkt.measurements.percentile_range import PercentileRange
from prenatalppkt.measurements.term_bin import TermBin

logger = logging.getLogger(__name__)

# Required biometry measurements - must be present in every file
REQUIRED_MEASUREMENTS = {"HC", "BPD", "AC", "Femur"}

# Optional biometry measurements - may not be present
OPTIONAL_MEASUREMENTS = {"Nuchal Fold", "Cerebellum", "OFD", "Humerus"}


class TermBinFactory:
    """
    Factory for creating TermBin objects from biometry measurements.

    Loads HPO mappings once and provides method to create TermBins
    using existing MeasurementEvaluation infrastructure.
    """

    def __init__(self, mappings_path: Optional[Path] = None):
        """
        Initialize factory with HPO mappings.

        Args:
            mappings_path: Path to YAML mappings file. If None, uses default.
        """
        self._mappings: Dict[str, List[TermBin]] = BiometryMappingLoader.load(
            mappings_path or self._get_default_mappings_path()
        )
        logger.info(f"Loaded HPO mappings for {len(self._mappings)} measurements")

    def create_term_bin(
        self,
        name: str,
        value_mm: float,
        percentile: float,
        gestational_age: Optional[GestationalAge] = None,
        method: Optional[str] = None,
        fetus_number: Optional[int] = None,
    ) -> Optional[TermBin]:
        """
        Create TermBin from raw measurement data.

        Args:
            name: Canonical measurement name (e.g., "HC", "BPD")
            value_mm: Measurement value in millimeters
            percentile: Percentile value (0-100 scale)
            gestational_age: GestationalAge object
            method: Measurement method (e.g., "Hadlock")
            fetus_number: Fetus identifier

        Returns:
            TermBin object or None if mapping fails

        Raises:
            ValueError: If percentile is out of range
        """
        # Validate percentile
        if not 0 <= percentile <= 100:
            raise ValueError(f"Percentile must be 0-100, got {percentile}")

        # Get measurement type for mapping lookup
        measurement_type = self._normalize_measurement_type(name)

        # Get configured TermBins for this measurement type
        if measurement_type not in self._mappings:
            logger.warning(f"No HPO mappings found for: {measurement_type}")
            return None

        configured_bins = self._mappings[measurement_type]

        # Use PercentileRange.evaluate() to determine bin
        target_range = PercentileRange.evaluate(percentile)

        # Find matching TermBin
        matching_bin = None
        for tb in configured_bins:
            if tb.range.bin_key == target_range.bin_key:
                matching_bin = tb
                break

        if not matching_bin:
            logger.warning(
                f"No TermBin matches percentile {percentile} "
                f"({target_range.bin_key}) for {name}"
            )
            return None

        # Build description
        description = self._build_description(
            name, value_mm, percentile, gestational_age, method, fetus_number
        )

        # Create TermBin using from_term() factory
        return TermBin.from_term(
            range=target_range,
            term=matching_bin.term,
            normal=matching_bin.normal,
            description=description,
        )

    def _normalize_measurement_type(self, name: str) -> str:
        """
        Normalize measurement name to match YAML mapping keys.

        Args:
            name: Canonical measurement name

        Returns:
            Normalized name for YAML lookup
        """
        name_map = {
            "HC": "head_circumference",
            "BPD": "biparietal_diameter",
            "AC": "abdominal_circumference",
            "Femur": "femur_length",
            "Nuchal Fold": "nuchal_fold",
            "Cerebellum": "cerebellum",
            "OFD": "occipitofrontal_diameter",
            "Humerus": "humerus_length",
        }
        return name_map.get(name, name.lower().replace(" ", "_"))

    def _build_description(
        self,
        name: str,
        value_mm: float,
        percentile: float,
        gestational_age: Optional[GestationalAge],
        method: Optional[str],
        fetus_number: Optional[int],
    ) -> str:
        """
        Build human-readable description for TermBin.

        Args:
            name: Measurement name
            value_mm: Value in mm
            percentile: Percentile value
            gestational_age: GA object
            method: Measurement method
            fetus_number: Fetus ID

        Returns:
            Formatted description string
        """
        parts = [f"{name}: {value_mm} mm", f"({percentile}%)"]

        if gestational_age:
            parts.append(f"at {gestational_age.weeks}w{gestational_age.days}d")

        if method:
            parts.append(f"({method})")

        if fetus_number is not None:
            parts.append(f"[Fetus {fetus_number}]")

        return " ".join(parts)

    def _get_default_mappings_path(self) -> Path:
        """Get path to default HPO mappings YAML."""
        package_root = Path(__file__).parents[3]
        return package_root / "data" / "mappings" / "biometry_hpo_mappings.yaml"


def validate_required_measurements(term_bins: List[TermBin]) -> None:
    """
    Validate that all required measurements are present.

    Args:
        term_bins: List of created TermBins

    Raises:
        ValueError: If any required measurement is missing
    """
    # Extract measurement names from TermBin descriptions
    present_measurements = set()
    for tb in term_bins:
        # Description format: "HC: 250.0 mm (42.5%) ..."
        name = tb.description.split(":")[0].strip()
        present_measurements.add(name)

    missing = REQUIRED_MEASUREMENTS - present_measurements

    if missing:
        error_msg = (
            f"Missing required biometry measurements: {', '.join(sorted(missing))}. "
            f"Required measurements are: {', '.join(sorted(REQUIRED_MEASUREMENTS))}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
