from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Union

from prenatalppkt.hpo import HpoParser


def parse_clinical_impression(
    data: Union[str, Dict], source_format: str, hpo_parser: Optional[HpoParser] = None
) -> Dict:
    """
    Parse clinical impression / interpretation section.

    Supports:
        - observer_json
        - viewpoint_text
        - viewpoint_hl7
    """
    if hpo_parser is None:
        hpo_parser = HpoParser()

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

    if impression_text and hasattr(hpo_parser, "extract"):
        hpo_terms = hpo_parser.extract(impression_text)
    else:
        hpo_terms = []

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
    exam = json_data.get("exam", {})
    finalize = exam.get("finalize", {})

    return finalize.get("generalComment", {}).get("plain_text", "").strip()


# ---------------------------------------------------------------------
# ViewPoint Text
# ---------------------------------------------------------------------


def _parse_viewpoint_text_impression(text: str) -> str:
    """
    Impression
    ==========
    Free text narrative
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
