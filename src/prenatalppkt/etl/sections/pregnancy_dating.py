"""
Pregnancy dating section parser (SKELETON).

TODO @VarenyaJ: Parse LMP, EDD, assigned dating method; Handle multiple dating methods (LMP, US, IVF)
"""

from typing import Dict


def parse_pregnancy_dating(data: str, source_format: str = "viewpoint_text") -> Dict:
    """Extract pregnancy dating information."""
    return {
        "lmp": None,
        "edd": None,
        "assigned_edd": None,
        "dating_method": None,
        "ga_by_lmp": None,
        "ga_by_ultrasound": None,
        "assigned_ga": None,
    }
