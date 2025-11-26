"""
Placenta section parser (SKELETON).

TODO @VarenyaJ: Parse placental location, grade, abnormalities
TODO @VarenyaJ: Map placental findings to HPO terms
"""

from typing import Dict


def parse_placenta(data: str, source_format: str = "viewpoint_text") -> Dict:
    """Extract placental assessment."""
    return {
        "location": None,
        "grade": None,
        "thickness_mm": None,
        "previa": False,
        "abnormalities": [],
        "hpo_terms": [],
    }
