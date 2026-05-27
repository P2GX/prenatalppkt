"""
extract_all.py

Walk both source corpora (CUIMC Observer JSON + EVMS GE HL7 v2.4),
classify every leaf path / OBX identifier into a cluster defined by
`clusters.yaml`, and emit one cross-source dictionary CSV at
`docs/data_dictionary/comparison.csv`.

One row per Observer leaf path; one row per HL7 OBX-3 identifier.
Cluster grouping comes from prefix matching against the curated
clusters.yaml; first match wins. Anything unmatched lands in the
`_unclustered` bucket.

Input:
prenatal-site-data/observer/center/CUIMC/pretty_print/*_pretty.json
prenatal-site-data/viewpoint/center/evms/GE_export_of_EVMS_test_cases/phenotype_*.txt
src/prenatalppkt/scripts/data_dict/clusters.yaml

Output:
prenatalppkt/docs/data_dictionary/comparison.csv

Dependencies:
PyYAML (already a prenatalppkt dep).
"""

from __future__ import annotations

import csv
import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# -----------------------
# Paths
# -----------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PPKT_ROOT = SCRIPT_DIR.parents[3]
PREGEN_ROOT = PPKT_ROOT.parent
OBSERVER_DIR = (
    PREGEN_ROOT
    / "prenatal-site-data"
    / "observer"
    / "center"
    / "CUIMC"
    / "pretty_print"
)
OBSERVER_GLOB = "*_pretty.json"
HL7_DIR = (
    PREGEN_ROOT
    / "prenatal-site-data"
    / "viewpoint"
    / "center"
    / "evms"
    / "GE_export_of_EVMS_test_cases"
)
HL7_GLOB = "phenotype_*.txt"
CLUSTERS_YAML = SCRIPT_DIR / "clusters.yaml"
OUT_CSV = PPKT_ROOT / "docs" / "data_dictionary" / "comparison.csv"


# -----------------------
# Metadata
# -----------------------

CSV_COLUMNS = [
    "cluster",
    "observer_path",
    "observer_type",
    "observer_sample",
    "observer_n_files",
    "viewpoint_path",
    "viewpoint_type",
    "viewpoint_sample",
    "viewpoint_n_files",
    "notes",
]

PERCENTILE_RE = re.compile(r"^(?:-?\d+(?:\.\d+)?%|[<>]\d+%)$")
WEEKS_DAYS_RE = re.compile(r"^\d+w \d+d$")
SAMPLE_LIMIT = 10
UNCLUSTERED = "_unclustered"


# -----------------------
# Type detection
# -----------------------


def detect_json_type(v: Any) -> str:
    """Classify one JSON value into a data-dictionary type token."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "dict"
    if isinstance(v, str):
        if PERCENTILE_RE.match(v):
            return "percentile_str"
        if WEEKS_DAYS_RE.match(v):
            return "weeks_days_str"
        return "str"
    return "str"


def detect_hl7_string_type(v: str) -> str:
    """Classify an HL7 OBX-5 string after the `^`-doubled normalization."""
    if v == "":
        return "null"
    return detect_json_type(v)


# -----------------------
# Cluster matching
# -----------------------


def load_clusters(path: Path) -> list[dict[str, Any]]:
    """Parse the clusters.yaml file into the list of cluster entries."""
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, list):
        raise ValueError(f"{path} must be a YAML list of cluster entries")
    return data


def classify_observer(path: str, clusters: list[dict[str, Any]]) -> str:
    """Return the cluster name for an Observer dotted path; first prefix match wins."""
    for entry in clusters:
        for prefix in entry.get("observer_prefixes", []):
            if path.startswith(prefix):
                return entry["cluster"]
    return UNCLUSTERED


def classify_viewpoint(identifier: str, clusters: list[dict[str, Any]]) -> str:
    """Return the cluster name for an HL7 OBX-3 primary identifier."""
    for entry in clusters:
        for prefix in entry.get("viewpoint_prefixes", []):
            if identifier.startswith(prefix):
                return entry["cluster"]
    return UNCLUSTERED


# -----------------------
# Observer walker
# -----------------------


def walk_observer(
    value: Any, path: str, file_id: str, acc: dict[str, dict[str, Any]]
) -> None:
    """Recursive descent over a JSON value; record per-path observations."""
    if path:
        record = acc[path]
        record.setdefault("observed_types", set()).add(detect_json_type(value))
        record.setdefault("files_present", set()).add(file_id)
        if value is not None and not isinstance(value, (list, dict)):
            samples: list[Any] = record.setdefault("value_set_sample", [])
            if value not in samples and len(samples) < SAMPLE_LIMIT:
                samples.append(value)
            elif value not in samples:
                record["value_overflow"] = True
    if isinstance(value, dict):
        for k, v in value.items():
            child = f"{path}.{k}" if path else k
            walk_observer(v, child, file_id, acc)
    elif isinstance(value, list):
        child = (path + "[]") if path else "[]"
        for elem in value:
            walk_observer(elem, child, file_id, acc)


def iter_observer_files() -> list[Path]:
    """Return sorted Observer JSON files in the corpus."""
    return sorted(OBSERVER_DIR.glob(OBSERVER_GLOB))


# -----------------------
# HL7 walker
# -----------------------


def primary_identifier(obx3: str) -> str:
    """First `^`-segment of an OBX-3 identifier triple."""
    return obx3.split("^", 1)[0]


def hl7_value_primary(obx5: str) -> str:
    """HL7 NM values are `^`-doubled; return the leading segment for sampling."""
    return obx5.split("^", 1)[0] if obx5 else obx5


def parse_obx_line(line: str) -> tuple[str, str, str] | None:
    """Pipe-split an `OBX|` line; return (obx_type, identifier, value) or None."""
    if not line.startswith("OBX|"):
        return None
    parts = line.rstrip("\r\n").split("|")
    if len(parts) < 6:
        return None
    return parts[2], parts[3], parts[5]


def walk_hl7_file(file_path: Path, acc: dict[str, dict[str, Any]]) -> int:
    """Parse one HL7 file; return the count of OBX rows seen."""
    count = 0
    with file_path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parsed = parse_obx_line(line)
            if parsed is None:
                continue
            obx_type, obx_identifier, obx_value = parsed
            primary = primary_identifier(obx_identifier)
            record = acc[primary]
            record.setdefault("hl7_obx_types", set()).add(obx_type)
            record.setdefault("observed_types", set()).add(
                detect_hl7_string_type(obx_value)
            )
            record.setdefault("files_present", set()).add(file_path.name)
            sample_value = hl7_value_primary(obx_value)
            if sample_value:
                samples: list[str] = record.setdefault("value_set_sample", [])
                if sample_value not in samples and len(samples) < SAMPLE_LIMIT:
                    samples.append(sample_value)
                elif sample_value not in samples:
                    record["value_overflow"] = True
            count += 1
    return count


def iter_hl7_files() -> list[Path]:
    """Return sorted EVMS GE HL7 files in the corpus."""
    return sorted(HL7_DIR.glob(HL7_GLOB))


# -----------------------
# Row formatting
# -----------------------


def format_types(record: dict[str, Any]) -> str:
    """Pipe-join the observed-type tokens in sorted order."""
    return "|".join(sorted(record.get("observed_types", set())))


def format_sample(record: dict[str, Any]) -> str:
    """Pipe-join up to SAMPLE_LIMIT distinct values; append `|...` if overflow."""
    samples = record.get("value_set_sample", [])
    if not samples:
        return ""
    formatted = "|".join(str(s) for s in samples)
    if record.get("value_overflow"):
        formatted += "|..."
    return formatted


def viewpoint_type_signature(record: dict[str, Any]) -> str:
    """Observed types annotated with the OBX-2 declared types in parens."""
    obs = format_types(record)
    hl7 = "|".join(sorted(record.get("hl7_obx_types", set())))
    if not hl7:
        return obs
    return f"{obs} ({hl7})" if obs else f"({hl7})"


def coverage(record: dict[str, Any], total: int) -> str:
    """Format the n_files_present cell as `present/total`."""
    return f"{len(record.get('files_present', set()))}/{total}"


# -----------------------
# Main
# -----------------------


def main() -> None:
    """Walk both corpora, classify, and emit comparison.csv."""
    clusters = load_clusters(CLUSTERS_YAML)
    observer_files = iter_observer_files()
    hl7_files = iter_hl7_files()
    if not observer_files:
        logger.error("No Observer JSONs at %s/%s", OBSERVER_DIR, OBSERVER_GLOB)
        raise SystemExit(1)
    if not hl7_files:
        logger.error("No HL7 files at %s/%s", HL7_DIR, HL7_GLOB)
        raise SystemExit(1)

    observer_acc: dict[str, dict[str, Any]] = defaultdict(dict)
    for f in observer_files:
        walk_observer(json.loads(f.read_text()), "", f.name, observer_acc)
        logger.info("Walked Observer file %s", f.name)

    hl7_acc: dict[str, dict[str, Any]] = defaultdict(dict)
    total_obx_rows = 0
    for f in hl7_files:
        total_obx_rows += walk_hl7_file(f, hl7_acc)
        logger.info("Walked HL7 file %s", f.name)

    rows: list[tuple[str, str, list[str]]] = []
    for path, rec in observer_acc.items():
        cluster = classify_observer(path, clusters)
        rows.append(
            (
                cluster,
                "obs",
                [
                    cluster,
                    path,
                    format_types(rec),
                    format_sample(rec),
                    coverage(rec, len(observer_files)),
                    "",
                    "",
                    "",
                    "",
                    "",
                ],
            )
        )
    for ident, rec in hl7_acc.items():
        cluster = classify_viewpoint(ident, clusters)
        rows.append(
            (
                cluster,
                "vp",
                [
                    cluster,
                    "",
                    "",
                    "",
                    "",
                    f"OBX {ident}",
                    viewpoint_type_signature(rec),
                    format_sample(rec),
                    coverage(rec, len(hl7_files)),
                    "",
                ],
            )
        )

    rows.sort(key=lambda r: (r[0], r[1], r[2][1] or r[2][5]))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(CSV_COLUMNS)
        for _cluster, _side, row in rows:
            writer.writerow(row)

    cluster_counts: dict[str, int] = defaultdict(int)
    for cluster, _side, _row in rows:
        cluster_counts[cluster] += 1

    logger.info("\n=== Parse Summary ===")
    logger.info("Observer files     : %d", len(observer_files))
    logger.info("HL7 files          : %d", len(hl7_files))
    logger.info("OBX rows parsed    : %d", total_obx_rows)
    logger.info("Observer leaf paths: %d", len(observer_acc))
    logger.info("HL7 identifiers    : %d", len(hl7_acc))
    logger.info("Rows written       : %d", len(rows))
    logger.info("Output             : %s", OUT_CSV)
    logger.info("\n=== Cluster Counts ===")
    for cluster in sorted(cluster_counts):
        logger.info("  %-25s : %d", cluster, cluster_counts[cluster])


if __name__ == "__main__":
    main()
