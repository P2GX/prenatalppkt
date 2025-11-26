"""
ViewPoint HL7 message biometry extractor.

Extracts fetal biometry measurements from ViewPoint HL7 message exports
and converts them directly to TermBin objects.

ViewPoint HL7 Format Characteristics:
   - **Field structure varies between messages** - not all segments always present
   - OBX segments contain measurements
   - Multi-segment format: measurement, percentile, GA, method in separate OBX lines
   - Measurements grouped by fetus identifier (e.g., |Fetus1|)

OBX Segment Structure:
   OBX|N|NM|MeasurementCode^Description||value|unit|||||

   Example sequence:
   OBX|57|NM|AbdomenFetus.AbdominalCircumference^AC||56|mm||||
   OBX|61|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|73^73%|%||||
   OBX|59|NM|AbdomenFetus.VP_AbdominalCircumference_GA|Fetus1|87^12w 3d|d||||

Measurement Codes:
   - HeadCircumference
   - BiParietalDiameter
   - AbdominalCircumference
   - FemurUndefinedLength or FemurLength
   - NuchalTranslucency (first trimester) or NuchalFold (second trimester)
   - Cerebellum (rare in HL7 exports)

Required Measurements: HC, BPD, AC, Femur (will ERROR if missing)
Optional Measurements: Nuchal Fold, Cerebellum, OFD, Humerus
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from prenatalppkt.etl.constants import VIEWPOINT_HL7_NAME_MAP
from prenatalppkt.etl.term_bin_factory import (
    TermBinFactory,
    validate_required_measurements,
)
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.term_bin import TermBin

logger = logging.getLogger(__name__)


def extract(data: str, factory: TermBinFactory = None) -> List[TermBin]:
    """
    Extract biometry measurements from ViewPoint HL7 and convert to TermBins.

    Args:
        data: ViewPoint HL7 message content as string
        factory: TermBinFactory instance (creates new if None)

    Returns:
        List of TermBin objects

    Raises:
        ValueError: If HL7 format is invalid or required measurements missing
    """
    if factory is None:
        factory = TermBinFactory()

    if not isinstance(data, str):
        raise ValueError(f"Expected string, got {type(data)}")

    # Parse OBX segments
    obx_segments = _extract_obx_segments(data)

    if not obx_segments:
        logger.warning("No OBX segments found in HL7 message")
        return []

    # Group measurements by fetus
    measurements_by_fetus = _group_measurements_by_fetus(obx_segments)

    # Convert to TermBins (process first fetus for now)
    term_bins = []
    if measurements_by_fetus:
        fetus_id = list(measurements_by_fetus.keys())[0]
        measurements = measurements_by_fetus[fetus_id]
        term_bins = _create_term_bins(measurements, factory)

    # Validate required measurements
    validate_required_measurements(term_bins)

    logger.info(f"Extracted {len(term_bins)} TermBins from ViewPoint HL7")
    return term_bins


def extract_from_file(filepath: Path, factory: TermBinFactory = None) -> List[TermBin]:
    """
    Extract biometry measurements from ViewPoint HL7 file.

    Args:
        filepath: Path to ViewPoint HL7 file
        factory: TermBinFactory instance (creates new if None)

    Returns:
        List of TermBin objects
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = f.read()

    return extract(data, factory)


def _extract_obx_segments(data: str) -> List[str]:
    """Extract all OBX segments from HL7 message."""
    lines = data.split("\n")
    return [line.strip() for line in lines if line.strip().startswith("OBX|")]


# Replace _group_measurements_by_fetus and add helper functions in viewpoint_hl7.py


def _group_measurements_by_fetus(obx_segments: List[str]) -> Dict[str, Dict[str, any]]:
    """
    Group measurement data by fetus.

    Returns:
        Dict mapping fetus_id -> {measurement_name -> {value, unit, percentile, ga, method}}
    """
    measurements = {}

    for segment in obx_segments:
        result = _process_obx_segment(segment)
        if result:
            fetus_id, measurement_name, field_type, value = result
            _store_measurement_field(
                measurements, fetus_id, measurement_name, field_type, value
            )

    return measurements


def _process_obx_segment(segment: str) -> Optional[Tuple[str, str, str, any]]:
    """Process single OBX segment and extract measurement info."""
    fields = segment.split("|")
    if len(fields) < 6:
        return None

    code = fields[3]
    fetus_id = fields[4] if len(fields) > 4 else "Fetus1"
    value_field = fields[5] if len(fields) > 5 else ""

    measurement_info = _parse_measurement_code(code)
    if not measurement_info:
        return None

    measurement_name, field_type = measurement_info
    value = _extract_field_value(field_type, value_field, fields)

    if value is None:
        return None

    return (fetus_id, measurement_name, field_type, value)


def _extract_field_value(
    field_type: str, value_field: str, fields: List[str]
) -> Optional[any]:
    """Extract value based on field type."""
    if field_type == "value":
        value = _parse_value(value_field)
        # Store unit if available
        if len(fields) > 6:
            return {"value": value, "unit": fields[6]}
        return value
    elif field_type == "percentile":
        return _parse_percentile_field(value_field)
    elif field_type == "ga":
        return _parse_ga_field(value_field)
    elif field_type == "author":
        return value_field
    return None


def _store_measurement_field(
    measurements: Dict,
    fetus_id: str,
    measurement_name: str,
    field_type: str,
    value: any,
):
    """Store measurement field in nested dict structure."""
    # Initialize fetus dict if needed
    if fetus_id not in measurements:
        measurements[fetus_id] = {}

    # Initialize measurement dict if needed
    if measurement_name not in measurements[fetus_id]:
        measurements[fetus_id][measurement_name] = {
            "value": None,
            "unit": None,
            "percentile": None,
            "ga": None,
            "method": None,
        }

    # Store value
    if field_type == "value" and isinstance(value, dict):
        measurements[fetus_id][measurement_name]["value"] = value.get("value")
        measurements[fetus_id][measurement_name]["unit"] = value.get("unit")
    else:
        measurements[fetus_id][measurement_name][field_type] = value


def _parse_measurement_code(code: str) -> Optional[Tuple[str, str]]:
    """
    Parse measurement code to extract name and field type.

    Args:
        code: OBX code field (e.g., "SkullFetus.HeadCircumference^HC")

    Returns:
        Tuple of (canonical_name, field_type) or None
    """
    # Extract measurement code (before ^)
    code_part = code.split("^")[0]

    # Determine field type
    if "_Percentile" in code_part:
        field_type = "percentile"
        base_code = code_part.replace("VP_", "").replace("_Percentile", "")
    elif "_GA" in code_part:
        field_type = "ga"
        base_code = code_part.replace("VP_", "").replace("_GA", "")
    elif "_Author" in code_part:
        field_type = "author"
        base_code = code_part.replace("VP_", "").replace("_Author", "")
    else:
        field_type = "value"
        base_code = code_part.split(".")[-1]  # Extract last part after dot

    # Map to canonical name
    if base_code in VIEWPOINT_HL7_NAME_MAP:
        canonical_name = VIEWPOINT_HL7_NAME_MAP[base_code].value
        return (canonical_name, field_type)

    return None


def _parse_value(value_field: str) -> Optional[float]:
    """Parse numeric value from HL7 field."""
    if not value_field:
        return None

    # Value might be "56^56.0" format
    value_str = value_field.split("^")[0]
    try:
        return float(value_str)
    except ValueError:
        return None


def _parse_percentile_field(value_field: str) -> Optional[float]:
    """
    Parse percentile from HL7 field.

    Format: "73^73%" or "0^<1%"
    """
    if not value_field:
        return None

    # Extract percentile string (after ^)
    parts = value_field.split("^")
    if len(parts) < 2:
        return None

    percentile_str = parts[1].rstrip("%")

    if percentile_str.startswith("<"):
        return 0.5
    elif percentile_str.startswith(">"):
        return 99.5

    try:
        return float(percentile_str)
    except ValueError:
        return None


def _parse_ga_field(value_field: str) -> Optional[GestationalAge]:
    """
    Parse gestational age from HL7 field.

    Format: "87^12w 3d" or "85^12w 1d"
    """
    if not value_field:
        return None

    # Extract GA string (after ^)
    parts = value_field.split("^")
    if len(parts) < 2:
        return None

    ga_str = parts[1]  # e.g., "12w 3d"

    # Parse weeks and days
    match = re.match(r"(\d+)w\s*(\d*)d?", ga_str)
    if not match:
        return None

    weeks = int(match.group(1))
    days = int(match.group(2)) if match.group(2) else 0

    return GestationalAge(weeks=weeks, days=days)


def _create_term_bins(
    measurements: Dict[str, Dict], factory: TermBinFactory
) -> List[TermBin]:
    """
    Create TermBins from parsed measurements.

    Args:
        measurements: Dict of {measurement_name -> {value, unit, percentile, ga, method}}
        factory: TermBinFactory instance

    Returns:
        List of TermBin objects
    """
    term_bins = []

    for name, data in measurements.items():
        value = data.get("value")
        percentile = data.get("percentile")

        if value is None or percentile is None:
            logger.debug(f"Skipping {name}: missing value or percentile")
            continue

        # Convert units
        unit = data.get("unit", "mm")
        value_mm = _convert_to_mm(value, unit)

        try:
            term_bin = factory.create_term_bin(
                name=name,
                value_mm=value_mm,
                percentile=percentile,
                gestational_age=data.get("ga"),
                method=data.get("method"),
                fetus_number=None,  # Could extract from MSH/PID if needed
            )
            if term_bin:
                term_bins.append(term_bin)
        except Exception as e:
            logger.warning(f"Failed to create TermBin for {name}: {e}")

    return term_bins


def _convert_to_mm(value: float, unit: str) -> float:
    """Convert measurement to millimeters."""
    unit_lower = unit.lower().strip()

    if unit_lower in ["mm", "millimeters", "millimeter"]:
        return value
    elif unit_lower in ["cm", "centimeters", "centimeter"]:
        return value * 10.0
    else:
        raise ValueError(f"Unsupported unit: {unit}")
