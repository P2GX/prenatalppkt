"""
TermBin factory for creating TermBin objects from raw biometry measurements.

This module provides a factory class that:

1. Loads HPO mappings once at initialization via BiometryMappingLoader
2. Treats the loaded TermBin objects as *configuration bins*:
    - range: PercentileRange
    - hpo_id: str
    - hpo_label: str
    - normal: bool
    - description: config-level description (e.g. "Below 3rd percentile")
3. Creates new *runtime* TermBin objects for specific measurements/percentiles
    - Keeps range / hpo_id / hpo_label / normal from the matching config bin
    - Builds a measurement-specific description string
4. Validates required measurements (HC, BPD, AC, Femur)
5. Handles optional measurements gracefully

Key design choice (Model B):

- YAML + BiometryMappingLoader.load() define static configuration TermBins.
- TermBinFactory is responsible for creating runtime TermBins that include
 measurement-specific context in their description.
"""

from __future__ import annotations

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

    Loads HPO mappings once and provides a method to create TermBins
    using existing percentile range infrastructure.

    BiometryMappingLoader.load() is expected to return a mapping:

        {
            "head_circumference": [
                TermBin(range=..., hpo_id="HP:0000252", hpo_label="Microcephaly", ...),
                TermBin(range=..., hpo_id="HP:0000240", hpo_label="Abnormality of skull size", ...),
                ...
            ],
            "femur_length": [...],
            ...
        }

    These loaded TermBins are treated as *configuration bins*; the factory
    uses them as templates but returns fresh TermBin instances whose
    descriptions encode the actual measurement, percentile, GA, method, etc.
    """

    def __init__(self, mappings_path: Optional[Path] = None):
        """
        Initialize factory with HPO mappings.

        Args:
            mappings_path:
                Path to YAML mappings file. If None, uses the default
                data/mappings/biometry_hpo_mappings.yaml at project root.
        """
        self._mappings: Dict[str, List[TermBin]] = BiometryMappingLoader.load(
            mappings_path or self._get_default_mappings_path()
        )
        logger.info("Loaded HPO mappings for %d measurements", len(self._mappings))

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

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
            name:
                Canonical measurement name (e.g., "HC", "BPD").
                Must match the canonical names used in BiometryMeasurement
                and YAML mappings (after normalization).
            value_mm:
                Measurement value in millimeters.
            percentile:
                Percentile value (0-100 scale).
            gestational_age:
                GestationalAge object (optional).
            method:
                Measurement method (e.g., "Hadlock") (optional).
            fetus_number:
                Fetus identifier (optional).

        Returns:
            TermBin object or None if mapping fails or percentile does not
            fall into any configured bin.

        Raises:
            ValueError:
                If percentile is out of the inclusive 0-100 range.
        """
        # Validate percentile
        if not 0 <= percentile <= 100:
            raise ValueError(f"Percentile must be 0-100, got {percentile}")

        # Normalize measurement name to the YAML mapping key
        measurement_type = self._normalize_measurement_type(name)

        # Get configured TermBins for this measurement type
        if measurement_type not in self._mappings:
            logger.warning("No HPO mappings found for: %s", measurement_type)
            return None

        configured_bins = self._mappings[measurement_type]

        # Determine which percentile bin this measurement belongs to
        target_range = PercentileRange.evaluate(percentile)

        # Find matching configuration TermBin (by bin_key)
        matching_bin: Optional[TermBin] = None
        for tb in configured_bins:
            if tb.range.bin_key == target_range.bin_key:
                matching_bin = tb
                break

        if not matching_bin:
            logger.warning(
                "No TermBin matches percentile %s (%s) for %s",
                percentile,
                target_range.bin_key,
                name,
            )
            return None

        # Build a measurement-specific description
        description = self._build_description(
            name=name,
            value_mm=value_mm,
            percentile=percentile,
            gestational_age=gestational_age,
            method=method,
            fetus_number=fetus_number,
        )

        # Create a new runtime TermBin using:
        #   - range from PercentileRange.evaluate (target_range)
        #   - hpo_id / hpo_label / normal from the config bin
        #   - contextual description we just built
        return TermBin(
            range=target_range,
            hpo_id=matching_bin.hpo_id,
            hpo_label=matching_bin.hpo_label,
            normal=matching_bin.normal,
            description=description,
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _normalize_measurement_type(self, name: str) -> str:
        """
        Normalize measurement name to match YAML mapping keys.

        Args:
            name:
                Canonical measurement name (e.g., "HC", "BPD", "Femur").

        Returns:
            Normalized name for YAML lookup (e.g., "head_circumference").
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

        Example:
            "HC: 250.0 mm (42.5%) at 27w1d (Hadlock) [Fetus 1]"
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
        """
        Get path to the default HPO mappings YAML.

        Expected location (relative to project root):
            data/mappings/biometry_hpo_mappings.yaml
        """
        package_root = Path(__file__).parents[3]
        return package_root / "data" / "mappings" / "biometry_hpo_mappings.yaml"


def validate_required_measurements(term_bins: List[TermBin]) -> None:
    """
    Validate that all required measurements are present.

    Args:
        term_bins:
            List of created TermBins.

    Raises:
        ValueError:
            If any required measurement is missing.
    """
    present_measurements = set()
    for tb in term_bins:
        # Description format begins with "NAME: ...", e.g., "HC: 250.0 mm ..."
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
