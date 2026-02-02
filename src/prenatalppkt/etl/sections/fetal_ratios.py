"""
Fetal ratios section parser.

Extracts biometric ratios (HC/AC, FL/BPD, FL/AC) and assesses proportionality.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Tuple, Union


def parse_fetal_ratios(data: Union[str, Dict], source_format: str) -> Dict:
    """
    Parse fetal ratios section.

    Supports:
        - observer_json
        - viewpoint_text (skeleton)
        - viewpoint_hl7 (skeleton)

    Args:
        data: Raw input data (JSON string, dict, or text)
        source_format: One of "observer_json", "viewpoint_text", "viewpoint_hl7"

    Returns:
        Dict with keys:
            - ratios: List[Dict] - Individual ratio data
            - all_within_range: bool - True if all ratios are normal
            - proportionality_assessment: str - "Normal" or "Asymmetric"
            - source_format: str
    """
    if source_format == "observer_json":
        if isinstance(data, str):
            data = json.loads(data)
        return _parse_observer_ratios(data)

    elif source_format == "viewpoint_text":
        if not isinstance(data, str):
            raise ValueError("viewpoint_text data must be a string")
        return _parse_viewpoint_text_ratios(data)

    elif source_format == "viewpoint_hl7":
        if not isinstance(data, str):
            raise ValueError("viewpoint_hl7 data must be a string")
        return _parse_viewpoint_hl7_ratios(data)

    else:
        raise ValueError(f"Unsupported source_format: {source_format}")


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


def _parse_observer_ratios(json_data: Dict) -> Dict:
    """
    Extract ratios from Observer JSON.

    Path: fetuses[i].ratios[]
    - label: str - ratio name (e.g., "HC/AC", "FL/BPD")
    - value: float - calculated ratio value
    - range: str - expected normal range (e.g., "1.04 - 1.22")
    - fetus_number: int
    """
    ratios: List[Dict] = []

    # Get first fetus
    fetuses = json_data.get("fetuses", [])
    if not fetuses:
        return _empty_result("observer_json")

    ratio_list = fetuses[0].get("ratios", [])
    if not ratio_list:
        return _empty_result("observer_json")

    all_within_range = True

    for ratio in ratio_list:
        label = ratio.get("label", "")
        value = ratio.get("value", 0)
        range_str = ratio.get("range", "")

        # Parse expected range
        expected_range = _parse_range_string(range_str)

        # Check if within range
        within_range = _is_within_range(value, expected_range)
        if not within_range:
            all_within_range = False

        ratios.append(
            {
                "name": label,
                "value": round(value, 3) if isinstance(value, float) else value,
                "expected_range": expected_range,
                "within_range": within_range,
            }
        )

    # Assess overall proportionality
    # Asymmetric growth typically indicated by abnormal HC/AC ratio
    proportionality = _assess_proportionality(ratios)

    return {
        "ratios": ratios,
        "all_within_range": all_within_range,
        "proportionality_assessment": proportionality,
        "source_format": "observer_json",
    }


# ---------------------------------------------------------------------
# ViewPoint Text (SKELETON)
# ---------------------------------------------------------------------


def _parse_viewpoint_text_ratios(text: str) -> Dict:
    """
    Extract ratios from ViewPoint text reports.

    Expected pattern (under Fetal Biometry section):
        FL / HC                    0.23

    TODO @VarenyaJ: : Implement full parsing
    """
    ratios: List[Dict] = []

    # Try to find ratio lines
    # Pattern: FL / HC   0.23
    ratio_pattern = re.compile(
        r"(FL|HC|AC|BPD)\s*/\s*(FL|HC|AC|BPD)\s+([\d.]+)", re.IGNORECASE
    )

    for match in ratio_pattern.finditer(text):
        name = f"{match.group(1).upper()}/{match.group(2).upper()}"
        value = float(match.group(3))
        ratios.append(
            {
                "name": name,
                "value": value,
                "expected_range": None,  # Not available in text format
                "within_range": None,
            }
        )

    return {
        "ratios": ratios,
        "all_within_range": None,  # Cannot assess without ranges
        "proportionality_assessment": "Unknown",
        "source_format": "viewpoint_text",
    }


# ---------------------------------------------------------------------
# ViewPoint HL7 (SKELETON)
# ---------------------------------------------------------------------


def _parse_viewpoint_hl7_ratios(hl7: str) -> Dict:
    """
    Extract ratios from HL7 ORU^R01 messages.

    Note: Ratios may not be present in all HL7 exports.
    This is a skeleton for potential future implementation.

    TODO @VarenyaJ: : Implement if HL7 ratio encoding is discovered
    """
    return _empty_result("viewpoint_hl7")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _parse_range_string(range_str: str) -> Optional[Tuple[float, float]]:
    """
    Parse a range string into a tuple.

    Examples:
        "1.04 - 1.22" -> (1.04, 1.22)
        "20 - 24" -> (20.0, 24.0)
        "" -> None
    """
    if not range_str:
        return None

    # Pattern: "min - max" or "min-max"
    match = re.match(r"([\d.]+)\s*-\s*([\d.]+)", range_str.strip())
    if match:
        return (float(match.group(1)), float(match.group(2)))

    return None


def _is_within_range(
    value: float, expected_range: Optional[Tuple[float, float]]
) -> Optional[bool]:
    """
    Check if a value is within the expected range.

    Returns None if range is not available.
    """
    if expected_range is None:
        return None

    min_val, max_val = expected_range
    return min_val <= value <= max_val


def _assess_proportionality(ratios: List[Dict]) -> str:
    """
    Assess overall fetal proportionality based on ratios.

    Asymmetric growth is typically indicated when:
    - HC/AC ratio is abnormal (head-sparing or brain-sparing pattern)
    - FL/AC ratio is abnormal
    """
    if not ratios:
        return "Unknown"

    # Check HC/AC specifically for asymmetric growth
    for ratio in ratios:
        if ratio["name"] == "HC/AC" and ratio["within_range"] is False:
            return "Asymmetric"

    # Check if all ratios with known ranges are within range
    ratios_with_ranges = [r for r in ratios if r["within_range"] is not None]
    if not ratios_with_ranges:
        return "Unknown"

    all_normal = all(r["within_range"] for r in ratios_with_ranges)
    return "Normal" if all_normal else "Asymmetric"


def _empty_result(source_format: str) -> Dict:
    """Return empty result structure."""
    return {
        "ratios": [],
        "all_within_range": None,
        "proportionality_assessment": "Unknown",
        "source_format": source_format,
    }
