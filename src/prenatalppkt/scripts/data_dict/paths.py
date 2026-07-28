"""
Shared path resolution for extract_all.py and render_readme.py.

Prefers the real EVMS/CUIMC data (external prenatal-site-data
checkout, sibling to this repo). When that checkout isn't present, falls
back to this repo's own synthetic fixtures under tests/data/, writing
output to `.local` suffixed files instead of the real filenames - so a
regeneration run without the real data never overwrites the real
data-derived comparison.csv/README.md/schema.md/clusters.md.
"""

from __future__ import annotations

from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PPKT_ROOT = SCRIPT_DIR.parents[3]
PREGEN_ROOT = PPKT_ROOT.parent
TEST_DATA_DIR = PPKT_ROOT / "tests" / "data"
DATA_DICT_DIR = PPKT_ROOT / "docs" / "data_dictionary"

_REAL_OBSERVER_DIR = (
    PREGEN_ROOT
    / "prenatal-site-data"
    / "observer"
    / "center"
    / "CUIMC"
    / "pretty_print"
)
_REAL_HL7_DIR = (
    PREGEN_ROOT
    / "prenatal-site-data"
    / "viewpoint"
    / "center"
    / "evms"
    / "GE_export_of_EVMS_test_cases"
)


def _has_matching_files(directory: Path, pattern: str) -> bool:
    """True only if the directory exists AND actually contains a file
    matching pattern - a directory that exists but is empty or not yet
    populated should fall through to the synthetic fixtures below, not
    be treated as usable real data."""
    return directory.is_dir() and any(directory.glob(pattern))


USING_REAL_DATA = _has_matching_files(
    _REAL_OBSERVER_DIR, "*_pretty.json"
) and _has_matching_files(_REAL_HL7_DIR, "phenotype_*.txt")

if USING_REAL_DATA:
    OBSERVER_DIR = _REAL_OBSERVER_DIR
    HL7_DIR = _REAL_HL7_DIR
    HL7_GLOBS = ["phenotype_*.txt"]
    _SUFFIX = ""
else:
    OBSERVER_DIR = TEST_DATA_DIR
    HL7_DIR = TEST_DATA_DIR
    HL7_GLOBS = ["viewpoint_hl7*.txt", "Discrete_HL7*.txt"]
    _SUFFIX = ".local"

OBSERVER_GLOB = "*_pretty.json"
OUT_CSV = DATA_DICT_DIR / f"comparison{_SUFFIX}.csv"
README_MD = DATA_DICT_DIR / f"README{_SUFFIX}.md"
SCHEMA_MD = DATA_DICT_DIR / f"schema{_SUFFIX}.md"
CLUSTERS_MD = DATA_DICT_DIR / f"clusters{_SUFFIX}.md"
