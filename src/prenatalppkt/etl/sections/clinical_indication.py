"""
Clinical indication section parser (SKELETON).

TODO @VarenyaJ: Map indications to ICD-10 and HPO terms
"""

from typing import Dict


def parse_clinical_indication(data: str, source_format: str = "viewpoint_text") -> Dict:
    """Extract indication for ultrasound exam."""
    return {"indication_text": "", "icd10_codes": [], "hpo_terms": []}
