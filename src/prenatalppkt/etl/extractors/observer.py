"""
Observer JSON biometry extractor.

Extracts fetal biometry measurements from Observer ultrasound system JSON exports
and converts them directly to TermBin objects.

Observer JSON Structure:
   - Consistent field structure across files
   - All fields reliably present in standard exports
   - Measurements in "fetuses" -> [fetus] -> "measurements" array

Format Characteristics:
   - Units: typically "cm" for most measurements, "mm" for Nuchal Fold
   - Percentiles: provided as floats (0-100 scale)
   - GA: provided as "calculated_ega" in weeks (float)
   - Fetus number: in "fetus" -> "fetus_number"

Required Measurements: HC, BPD, AC, Femur (will ERROR if missing)
Optional Measurements: Nuchal Fold, Cerebellum, OFD, Humerus
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from prenatalppkt.etl.constants import OBSERVER_NAME_MAP
from prenatalppkt.etl.term_bin_factory import (
    TermBinFactory,
    validate_required_measurements,
)
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.term_bin import TermBin

logger = logging.getLogger(__name__)


def extract(data: Dict[str, Any], factory: TermBinFactory = None) -> List[TermBin]:
    """
    Extract biometry measurements from Observer JSON and convert to TermBins.

    Args:
        data: Parsed Observer JSON dictionary
        factory: TermBinFactory instance (creates new if None)

    Returns:
        List of TermBin objects

    Raises:
        ValueError: If JSON structure is invalid or required measurements missing
    """
    if factory is None:
        factory = TermBinFactory()

    # Validate structure
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict, got {type(data)}")

    if "fetuses" not in data:
        raise ValueError("Missing 'fetuses' key in Observer JSON")

    fetuses = data["fetuses"]
    if not fetuses or not isinstance(fetuses, list):
        raise ValueError("'fetuses' must be non-empty list")

    # Extract from first fetus (can extend for multiple fetuses)
    fetus_data = fetuses[0]
    fetus_number = _get_fetus_number(fetus_data)

    # Parse measurements into TermBins
    term_bins = _parse_measurements(fetus_data, fetus_number, factory)

    # Validate required measurements present
    validate_required_measurements(term_bins)

    logger.info(f"Extracted {len(term_bins)} TermBins from Observer JSON")
    return term_bins


def extract_from_file(filepath: Path, factory: TermBinFactory = None) -> List[TermBin]:
    """
    Extract biometry measurements from Observer JSON file.

    Args:
        filepath: Path to Observer JSON file
        factory: TermBinFactory instance (creates new if None)

    Returns:
        List of TermBin objects
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return extract(data, factory)


def _get_fetus_number(fetus_data: Dict[str, Any]) -> int:
    """Extract fetus number from fetus data."""
    fetus_section = fetus_data.get("fetus", {})
    return fetus_section.get("fetus_number", 1)


def _parse_measurements(
    fetus_data: Dict[str, Any], fetus_number: int, factory: TermBinFactory
) -> List[TermBin]:
    """
    Parse measurements and convert to TermBins.

    Args:
        fetus_data: Single fetus dictionary
        fetus_number: Fetus identifier
        factory: TermBinFactory instance

    Returns:
        List of TermBin objects
    """
    if "measurements" not in fetus_data:
        logger.warning("No 'measurements' key in fetus data")
        return []

    measurements_list = fetus_data["measurements"]
    if not isinstance(measurements_list, list):
        raise ValueError("'measurements' must be a list")

    term_bins = []
    for m in measurements_list:
        try:
            term_bin = _parse_single_measurement(m, fetus_number, factory)
            if term_bin:
                term_bins.append(term_bin)
        except Exception as e:  # noqa: PERF203
            logger.warning(
                f"Failed to parse measurement {m.get('label', 'unknown')}: {e}"
            )

    return term_bins


def _parse_single_measurement(
    m: Dict[str, Any], fetus_number: int, factory: TermBinFactory
) -> TermBin:
    """
    Parse single measurement into TermBin.

    Args:
        m: Measurement dictionary
        fetus_number: Fetus identifier
        factory: TermBinFactory instance

    Returns:
        TermBin object or None if not a target measurement
    """
    label = m.get("label")
    if not label:
        return None

    # Check if target measurement
    if label not in OBSERVER_NAME_MAP:
        return None

    # Normalize label to canonical name
    canonical_name = OBSERVER_NAME_MAP[label].value

    # Extract required fields
    value = m.get("value")
    if value is None:
        logger.debug(f"Skipping {label}: no value")
        return None

    # Extract optional fields
    unit = m.get("unit_of_measure", "cm")
    percentile = m.get("calculated_percentile")
    ega = m.get("calculated_ega")

    # Must have percentile to create TermBin
    if percentile is None:
        logger.warning(f"Skipping {label}: no percentile")
        return None

    # Convert units
    value_mm = _convert_to_mm(float(value), unit)

    # Parse gestational age
    gestational_age = None
    if ega is not None:
        gestational_age = GestationalAge.from_weeks(float(ega))

    # Create TermBin using factory
    return factory.create_term_bin(
        name=canonical_name,
        value_mm=value_mm,
        percentile=float(percentile),
        gestational_age=gestational_age,
        method=None,  # Observer JSON doesn't include method
        fetus_number=fetus_number,
    )


def _convert_to_mm(value: float, unit: str) -> float:
    """
    Convert measurement to millimeters.

    Args:
        value: Measurement value
        unit: Unit of measure

    Returns:
        Value in millimeters

    Raises:
        ValueError: If unit not supported
    """
    unit_lower = unit.lower().strip()

    if unit_lower in ["mm", "millimeters", "millimeter"]:
        return value
    elif unit_lower in ["cm", "centimeters", "centimeter"]:
        return value * 10.0
    else:
        raise ValueError(f"Unsupported unit: {unit}")
