"""
Fetal anatomy section parser.

Extracts structured anatomy findings and free-text anatomy narrative,
with optional HPO term extraction from anomaly descriptions.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Union


def parse_fetal_anatomy(
    data: Union[str, Dict], source_format: str, hpo_cr=None
) -> Dict:
    """
    Parse fetal anatomy section.

    Supports:
        - observer_json
        - viewpoint_text (skeleton)
        - viewpoint_hl7 (skeleton)

    Args:
        data: Raw input data (JSON string, dict, or text)
        source_format: One of "observer_json", "viewpoint_text", "viewpoint_hl7"
        hpo_cr: Optional HpoExactConceptRecognizer for HPO term extraction.
                If provided, will extract HPO terms from anomaly descriptions.

    Returns:
        Dict with keys:
            - anatomy_text: str - Free text anatomy narrative
            - normal_structures: List[str] - Structures marked Normal
            - abnormal_structures: List[str] - Structures marked Abnormal
            - not_visualized: List[str] - Structures marked Unseen
            - anomalies: List[Dict] - Specific anomaly findings
            - hpo_terms: List[SimpleTerm] - HPO terms extracted via CR
            - source_format: str
    """
    if source_format == "observer_json":
        if isinstance(data, str):
            data = json.loads(data)
        return _parse_observer_anatomy(data, hpo_cr)

    elif source_format == "viewpoint_text":
        if not isinstance(data, str):
            raise ValueError("viewpoint_text data must be a string")
        return _parse_viewpoint_text_anatomy(data, hpo_cr)

    elif source_format == "viewpoint_hl7":
        if not isinstance(data, str):
            raise ValueError("viewpoint_hl7 data must be a string")
        return _parse_viewpoint_hl7_anatomy(data, hpo_cr)

    else:
        raise ValueError(f"Unsupported source_format: {source_format}")


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


def _classify_structure(
    label: str, state: str, normal: List[str], abnormal: List[str], unseen: List[str]
) -> None:
    """Classify a structure into the appropriate list based on state."""
    if not label:
        return
    if state == "Normal" and label not in normal:
        normal.append(label)
    elif state == "Abnormal" and label not in abnormal:
        abnormal.append(label)
    elif state == "Unseen" and label not in unseen:
        unseen.append(label)


def _process_anatomy_item(
    item: Dict,
    normal: List[str],
    abnormal: List[str],
    unseen: List[str],
    anomalies: List[Dict],
) -> None:
    """Process a single anatomy item, extracting structures and anomalies."""
    main = item.get("main", {})
    label = main.get("label", "")
    state = main.get("anat_state", "")

    # Classify main structure
    _classify_structure(label, state, normal, abnormal, unseen)

    # Process detail sub-structures
    for detail in item.get("detail", []):
        detail_label = detail.get("label", "")
        detail_state = detail.get("anat_det_state", "")
        _classify_structure(detail_label, detail_state, normal, abnormal, unseen)

    # Process anomalies
    for anom in item.get("anomalies", []):
        description = anom.get("description", "")
        if description:
            anomalies.append(
                {
                    "structure": label,
                    "description": description,
                    "variant_type": anom.get("abnormal_or_normal_variant", "Abnormal"),
                }
            )


def _extract_hpo_terms(anatomy_text: str, anomalies: List[Dict], hpo_cr) -> List:
    """Extract HPO terms from anatomy text and anomaly descriptions."""
    if hpo_cr is None or not hasattr(hpo_cr, "parse"):
        return []

    all_anomaly_text = " ".join(
        a["description"] for a in anomalies if a.get("description")
    )
    combined_text = f"{anatomy_text} {all_anomaly_text}".strip()

    if not combined_text:
        return []

    return hpo_cr.parse(combined_text)


def _parse_observer_anatomy(json_data: Dict, hpo_cr=None) -> Dict:
    """
    Extract anatomy findings from Observer JSON.

    Paths:
    - fetuses[i].fetus.anatomy_text - free text narrative
    - fetuses[i].fetus.anatomy[] - structured findings
      - main.label - structure name (e.g., "Head", "Face")
      - main.anat_state - "Normal", "Abnormal", or "Unseen"
      - detail[].label - sub-structure name
      - detail[].anat_det_state - sub-structure state
      - anomalies[].description - specific finding text
      - anomalies[].abnormal_or_normal_variant - classification
    """
    fetuses = json_data.get("fetuses", [])
    if not fetuses:
        return _empty_result("observer_json")

    fetus_block = fetuses[0].get("fetus", {})
    anatomy_text = fetus_block.get("anatomy_text", "")

    normal_structures: List[str] = []
    abnormal_structures: List[str] = []
    not_visualized: List[str] = []
    anomalies: List[Dict] = []

    for item in fetus_block.get("anatomy", []):
        _process_anatomy_item(
            item, normal_structures, abnormal_structures, not_visualized, anomalies
        )

    hpo_terms = _extract_hpo_terms(anatomy_text, anomalies, hpo_cr)

    return {
        "anatomy_text": anatomy_text,
        "normal_structures": normal_structures,
        "abnormal_structures": abnormal_structures,
        "not_visualized": not_visualized,
        "anomalies": anomalies,
        "hpo_terms": hpo_terms,
        "source_format": "observer_json",
    }


# ---------------------------------------------------------------------
# ViewPoint Text (SKELETON)
# ---------------------------------------------------------------------


def _parse_viewpoint_text_anatomy(text: str, hpo_cr=None) -> Dict:
    """
    Extract anatomy from ViewPoint text reports.

    Expected pattern:
        Fetal Anatomy
        =============
        The following structures appear normal:
        Cranium. Brain. Face. ...

        The following structures appear abnormal:
        GI tract: dilated bowel loops.

        The following structures could not be adequately visualized:
        LVOT view. RVOT view. ...

    TODO @VarenyaJ: Implement full parsing
    """
    # Skeleton: Extract the Fetal Anatomy section
    pattern = re.compile(
        r"Fetal Anatomy\s*\n=+\n(?P<body>.*?)(?:\n[A-Z][^\n]*\n=+|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(text)
    anatomy_text = match.group("body").strip() if match else ""

    # TODO @VarenyaJ: Parse "appear normal", "appear abnormal", "could not be visualized" lists

    hpo_terms = []
    if anatomy_text and hpo_cr is not None and hasattr(hpo_cr, "parse"):
        hpo_terms = hpo_cr.parse(anatomy_text)

    return {
        "anatomy_text": anatomy_text,
        "normal_structures": [],
        "abnormal_structures": [],
        "not_visualized": [],
        "anomalies": [],
        "hpo_terms": hpo_terms,
        "source_format": "viewpoint_text",
    }


# ---------------------------------------------------------------------
# ViewPoint HL7 (SKELETON)
# ---------------------------------------------------------------------


def _parse_viewpoint_hl7_anatomy(hl7: str, hpo_cr=None) -> Dict:
    """
    Extract anatomy from HL7 ORU^R01 messages.

    Note: Anatomy is typically not encoded in discrete HL7 fields.
    This is a skeleton for potential future implementation.

    TODO @VarenyaJ: Implement if HL7 anatomy encoding is discovered
    """
    return _empty_result("viewpoint_hl7")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _empty_result(source_format: str) -> Dict:
    """Return empty result structure."""
    return {
        "anatomy_text": "",
        "normal_structures": [],
        "abnormal_structures": [],
        "not_visualized": [],
        "anomalies": [],
        "hpo_terms": [],
        "source_format": source_format,
    }
