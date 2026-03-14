"""
Estimated fetal weight (EFW) section parser.

Extracts EFW values, percentiles, and growth classification.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Union


def parse_estimated_fetal_weight(data: Union[str, Dict], source_format: str) -> Dict:
    """
    Parse estimated fetal weight section.

    Supports:
        - observer_json
        - viewpoint_text (skeleton)
        - viewpoint_hl7 (skeleton)

    Args:
        data: Raw input data (JSON string, dict, or text)
        source_format: One of "observer_json", "viewpoint_text", "viewpoint_hl7"

    Returns:
        Dict with keys:
            - efw_grams: float - Primary EFW value in grams
            - percentile: float - Percentile for primary EFW
            - method: str - Calculation method (e.g., "Hadlock (AC, FL, HC)")
            - within_normal_range: bool - True if 10th-90th percentile
            - growth_category: str - "SGA", "AGA", or "LGA"
            - all_estimates: List[Dict] - All EFW calculations
            - source_format: str
    """
    if source_format == "observer_json":
        if isinstance(data, str):
            data = json.loads(data)
        return _parse_observer_efw(data)

    elif source_format == "viewpoint_text":
        if not isinstance(data, str):
            raise ValueError("viewpoint_text data must be a string")
        return _parse_viewpoint_text_efw(data)

    elif source_format == "viewpoint_hl7":
        if not isinstance(data, str):
            raise ValueError("viewpoint_hl7 data must be a string")
        return _parse_viewpoint_hl7_efw(data)

    else:
        raise ValueError(f"Unsupported source_format: {source_format}")


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


def _parse_observer_efw(json_data: Dict) -> Dict:
    """
    Extract EFW from Observer JSON.

    Path: fetuses[i].efws[]
    - fetus_number: int
    - label: str - method description (e.g., "EFW (AC, FL, HC)")
    - value: float - weight in grams
    - calculated_percentile: float
    - percentile_for_display: str
    - print_in_report: int - 1 if this is the primary EFW
    - range: str - optional expected range
    """
    all_estimates: List[Dict] = []
    primary_efw: Optional[Dict] = None

    # Get first fetus
    fetuses = json_data.get("fetuses", [])
    if not fetuses:
        return _empty_result("observer_json")

    efws = fetuses[0].get("efws", [])
    if not efws:
        return _empty_result("observer_json")

    for efw in efws:
        label = efw.get("label", "")
        value = efw.get("value", 0)
        percentile = efw.get("calculated_percentile", 0)
        print_in_report = efw.get("print_in_report", 0)

        # Extract method from label (e.g., "EFW (AC, FL, HC)" -> "AC, FL, HC")
        method = _extract_method_from_label(label)

        estimate = {
            "method": method,
            "grams": round(value, 1),
            "percentile": round(percentile, 1),
            "print_in_report": bool(print_in_report),
        }
        all_estimates.append(estimate)

        # Select primary EFW (print_in_report=1 or first one)
        if print_in_report == 1 and primary_efw is None:
            primary_efw = estimate

    # Fallback to first estimate if none marked for report
    if primary_efw is None and all_estimates:
        primary_efw = all_estimates[0]

    if primary_efw is None:
        return _empty_result("observer_json")

    # Classify growth
    percentile = primary_efw["percentile"]
    growth_category = _classify_growth(percentile)
    within_normal = 10 <= percentile <= 90

    return {
        "efw_grams": primary_efw["grams"],
        "percentile": primary_efw["percentile"],
        "method": primary_efw["method"],
        "within_normal_range": within_normal,
        "growth_category": growth_category,
        "all_estimates": all_estimates,
        "source_format": "observer_json",
    }


# ---------------------------------------------------------------------
# ViewPoint Text (SKELETON)
# ---------------------------------------------------------------------


def _parse_viewpoint_text_efw(text: str) -> Dict:
    """
    Extract EFW from ViewPoint text reports.

    Expected patterns:
        EFW                    2,042    g                    2%
        EFW (lb,oz)           4 lb 8    oz
        EFW by                Hadlock (BPD-HC-AC-FL)

    TODO @VarenyaJ: Implement full parsing
    """
    efw_grams = None
    percentile = None
    method = None

    # Try to find EFW line with grams
    efw_pattern = re.compile(r"EFW\s+([0-9,]+)\s+g\s+(\d+)%", re.IGNORECASE)
    match = efw_pattern.search(text)
    if match:
        efw_grams = float(match.group(1).replace(",", ""))
        percentile = float(match.group(2))

    # Try to find method
    method_pattern = re.compile(r"EFW by\s+(.+)", re.IGNORECASE)
    method_match = method_pattern.search(text)
    if method_match:
        method = method_match.group(1).strip()

    if efw_grams is None:
        return _empty_result("viewpoint_text")

    growth_category = _classify_growth(percentile) if percentile else "Unknown"
    within_normal = 10 <= percentile <= 90 if percentile else False

    return {
        "efw_grams": efw_grams,
        "percentile": percentile,
        "method": method or "Unknown",
        "within_normal_range": within_normal,
        "growth_category": growth_category,
        "all_estimates": [
            {
                "method": method or "Unknown",
                "grams": efw_grams,
                "percentile": percentile,
            }
        ],
        "source_format": "viewpoint_text",
    }


# ---------------------------------------------------------------------
# ViewPoint HL7 (SKELETON)
# ---------------------------------------------------------------------


def _parse_viewpoint_hl7_efw(hl7: str) -> Dict:
    """
    Extract EFW from HL7 ORU^R01 messages.

    Note: EFW may not be present in all HL7 exports.
    This is a skeleton for potential future implementation.

    TODO @VarenyaJ: Implement if HL7 EFW encoding is discovered
    """
    return _empty_result("viewpoint_hl7")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _extract_method_from_label(label: str) -> str:
    """
    Extract method from EFW label.

    Examples:
        "EFW (AC, FL, HC)" -> "Hadlock (AC, FL, HC)"
        "EFW (AC, FL)" -> "Hadlock (AC, FL)"
    """
    match = re.search(r"\(([^)]+)\)", label)
    if match:
        params = match.group(1)
        return f"Hadlock ({params})"
    return "Hadlock"


def _classify_growth(percentile: float) -> str:
    """
    Classify fetal growth based on EFW percentile.

    - SGA (Small for Gestational Age): <10th percentile
    - AGA (Appropriate for Gestational Age): 10th-90th percentile
    - LGA (Large for Gestational Age): >90th percentile
    """
    if percentile < 10:
        return "SGA"
    elif percentile > 90:
        return "LGA"
    else:
        return "AGA"


def _empty_result(source_format: str) -> Dict:
    """Return empty result structure."""
    return {
        "efw_grams": None,
        "percentile": None,
        "method": None,
        "within_normal_range": None,
        "growth_category": None,
        "all_estimates": [],
        "source_format": source_format,
    }
