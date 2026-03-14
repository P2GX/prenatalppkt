"""
Clinical impression / interpretation section parser.

Extracts clinical narrative text and optionally extracts HPO terms
from free text using the HPO Concept Recognizer.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Union


def parse_clinical_impression(
    data: Union[str, Dict], source_format: str, hpo_cr=None
) -> Dict:
    """
    Parse clinical impression / interpretation section.

    Supports:
        - observer_json
        - viewpoint_text
        - viewpoint_hl7

    Args:
        data: Raw input data (JSON string, dict, or text)
        source_format: One of "observer_json", "viewpoint_text", "viewpoint_hl7"
        hpo_cr: Optional HpoExactConceptRecognizer for HPO term extraction.
                If provided, will extract HPO terms from impression text.

    Returns:
        Dict with keys:
            - impression_text: str - Full impression narrative
            - diagnoses: List[str] - Identified diagnoses (future)
            - anomalies: List[Dict] - Structured anomaly data (future)
            - gestational_age_assessment: Optional[str] - GA conclusion
            - growth_assessment: Optional[str] - FGR, LGA, AGA, or None
            - recommendations: List[str] - Follow-up recommendations (future)
            - hpo_terms: List[SimpleTerm] - HPO terms extracted via CR
            - source_format: str
    """
    if source_format == "observer_json":
        if isinstance(data, str):
            data = json.loads(data)
        impression_text = _parse_observer_impression(data)

    elif source_format == "viewpoint_text":
        if not isinstance(data, str):
            raise ValueError("viewpoint_text data must be a string")
        impression_text = _parse_viewpoint_text_impression(data)

    elif source_format == "viewpoint_hl7":
        if not isinstance(data, str):
            raise ValueError("viewpoint_hl7 data must be a string")
        impression_text = _parse_viewpoint_hl7_impression(data)

    else:
        raise ValueError(f"Unsupported source_format: {source_format}")

    # Extract HPO terms if concept recognizer is provided
    hpo_terms = []
    if impression_text and hpo_cr is not None:
        # HpoExactConceptRecognizer uses parse() method, not extract()
        if hasattr(hpo_cr, "parse"):
            hpo_terms = hpo_cr.parse(impression_text)

    return {
        "impression_text": impression_text,
        "diagnoses": [],
        "anomalies": [],
        "gestational_age_assessment": None,
        "growth_assessment": _infer_growth_assessment(impression_text),
        "recommendations": [],
        "hpo_terms": hpo_terms,
        "source_format": source_format,
    }


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


def _parse_observer_impression(json_data: Dict) -> str:
    """
    Extract impression from Observer JSON.

    The finalize block can be at:
    - Root level: json_data["finalize"]["generalComment"]["plain_text"]
    - Under exam: json_data["exam"]["finalize"]["generalComment"]["plain_text"]

    We check the root level first (most common), then fall back to exam.
    """
    impression = ""

    # Check root level first (this is where Apple_Sally has it)
    finalize = json_data.get("finalize", {})
    impression = finalize.get("generalComment", {}).get("plain_text", "").strip()

    # Fall back to exam.finalize if not found at root
    if not impression:
        exam = json_data.get("exam", {})
        finalize = exam.get("finalize", {})
        impression = finalize.get("generalComment", {}).get("plain_text", "").strip()

    return impression


# ---------------------------------------------------------------------
# ViewPoint Text
# ---------------------------------------------------------------------


def _parse_viewpoint_text_impression(text: str) -> str:
    """
    Extract impression from ViewPoint text reports.

    Expected pattern:
        Impression
        ==========
        [free text narrative]
    """
    pattern = re.compile(
        r"Impression\s*\n=+\n(?P<body>.*?)(?:\n[A-Z][^\n]*\n=+|\Z)",
        re.DOTALL | re.IGNORECASE,
    )

    match = pattern.search(text)
    return match.group("body").strip() if match else ""


# ---------------------------------------------------------------------
# ViewPoint HL7
# ---------------------------------------------------------------------


def _parse_viewpoint_hl7_impression(hl7: str) -> str:
    """
    Extract impression from HL7 ORU^R01 messages.

    Looks for OBX segments containing "Impression" or "Interpretation"
    in the observation identifier field.
    """
    lines: List[str] = []

    for line in hl7.splitlines():
        if not line.startswith("OBX"):
            continue

        fields = line.split("|")
        if len(fields) < 6:
            continue

        obs_id = fields[3]
        value = fields[5].split("^")[0].strip()

        if "Impression" in obs_id or "Interpretation" in obs_id:
            if value:
                lines.append(value)

    return " ".join(lines)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _infer_growth_assessment(text: str) -> Optional[str]:
    """
    Infer fetal growth assessment from impression text.

    Returns:
        "FGR" - Fetal Growth Restriction
        "LGA" - Large for Gestational Age
        "AGA" - Appropriate for Gestational Age
        None - No assessment detected
    """
    if not text:
        return None

    text_lower = text.lower()

    if "growth restriction" in text_lower or "fgr" in text_lower:
        return "FGR"
    if "large for gestational age" in text_lower or "lga" in text_lower:
        return "LGA"
    if "appropriate for gestational age" in text_lower or "aga" in text_lower:
        return "AGA"

    return None
