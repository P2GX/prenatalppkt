from __future__ import annotations

import json
import re
from typing import Dict, List, Union


def parse_clinical_indication(data: Union[str, Dict], source_format: str) -> Dict:
    """
    Parse clinical indication / reason for exam from different source formats.

    Supported formats:
        - observer_json
        - viewpoint_text
        - viewpoint_hl7

    Returns a normalized Dict with indication metadata.
    """
    if source_format == "observer_json":
        if isinstance(data, str):
            data = json.loads(data)
        result = _parse_observer_indication(data)

    elif source_format == "viewpoint_text":
        if not isinstance(data, str):
            raise ValueError("viewpoint_text data must be a string")
        result = _parse_viewpoint_text_indication(data)

    elif source_format == "viewpoint_hl7":
        if not isinstance(data, str):
            raise ValueError("viewpoint_hl7 data must be a string")
        result = _parse_viewpoint_hl7_indication(data)

    else:
        raise ValueError(f"Unsupported source_format: {source_format}")

    # Standardized return schema
    result.setdefault("icd10_codes", [])
    result.setdefault("hpo_terms", [])
    result["source_format"] = source_format
    return result


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


def _parse_observer_indication(json_data: Dict) -> Dict:
    """
    Extract indication from Observer JSON.
    Known locations:
        - exam.indication
        - exam.finalize.indication
    """
    indication_text = ""

    exam = json_data.get("exam", {})
    if isinstance(exam, dict):
        indication_text = (
            exam.get("indication") or exam.get("finalize", {}).get("indication") or ""
        )

    return {"indication_text": indication_text.strip(), "raw_data": json_data}


# ---------------------------------------------------------------------
# ViewPoint Text
# ---------------------------------------------------------------------


def _parse_viewpoint_text_indication(text: str) -> Dict:
    """
    Extract indication section from ViewPoint text reports.

    Expected pattern:
        Indication
        ==========
        [free text]
    """
    indication_text = ""

    pattern = re.compile(
        r"Indication\s*\n=+\n(?P<body>.*?)(?:\n[A-Z][^\n]*\n=+|\Z)",
        re.DOTALL | re.IGNORECASE,
    )

    match = pattern.search(text)
    if match:
        indication_text = match.group("body").strip()

    return {"indication_text": indication_text, "raw_data": {"text": text}}


# ---------------------------------------------------------------------
# ViewPoint HL7
# ---------------------------------------------------------------------


def _parse_viewpoint_hl7_indication(hl7: str) -> Dict:
    """
    Extract indication from HL7 ORU^R01 messages.

    Common pattern:
        OBX||ST|RequestedProcedure.Indication^Indication|1|Advanced maternal age
    """
    indication_lines: List[str] = []

    for line in hl7.splitlines():
        if not line.startswith("OBX"):
            continue

        fields = line.split("|")
        if len(fields) < 6:
            continue

        observation_id = fields[3]
        value_field = fields[5]

        if "RequestedProcedure.Indication" in observation_id:
            # HL7 values may be caret-delimited
            value = value_field.split("^")[0]
            if value:
                indication_lines.append(value.strip())

    indication_text = " ".join(indication_lines)

    return {"indication_text": indication_text, "raw_data": {"hl7": hl7}}
