"""
extract_all.py

Walk both source corpora (CUIMC Observer JSON + EVMS GE HL7 v2.4),
attach a per-row semantic value class, propagate Observer list
labels (so `fetuses[].measurements[].value` splits into one row per
label: BPD / AC / HC / Femur / ...), pair Observer rows with HL7
rows that share a label token and a compatible value class, and
emit one cross-source dictionary CSV at
`docs/data_dictionary/comparison.csv`.

Inputs:
    prenatal-site-data/observer/center/CUIMC/pretty_print/*_pretty.json
    prenatal-site-data/viewpoint/center/evms/GE_export_of_EVMS_test_cases/phenotype_*.txt
    src/prenatalppkt/scripts/data_dict/clusters.yaml

Output:
    prenatalppkt/docs/data_dictionary/comparison.csv (16 columns;
    the first column is `concept_key`, populated by looking up each
    row against `concept_aliases.yaml`).
"""

from __future__ import annotations

import csv
import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
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
CONCEPT_ALIASES_YAML = SCRIPT_DIR / "concept_aliases.yaml"
OUT_CSV = PPKT_ROOT / "docs" / "data_dictionary" / "comparison.csv"


# -----------------------
# Metadata
# -----------------------

CSV_COLUMNS = [
    "concept_key",
    "cluster",
    "observer_path",
    "observer_label_values",
    "observer_type",
    "observer_value_class",
    "observer_sample",
    "observer_n_files",
    "viewpoint_path",
    "viewpoint_short_label",
    "viewpoint_long_label",
    "viewpoint_type",
    "viewpoint_value_class",
    "viewpoint_sample",
    "viewpoint_n_files",
    "notes",
]

SAMPLE_LIMIT = 10
UNCLUSTERED = "_unclustered"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{8}$")
TIME_RE = re.compile(r"^\d{6}$")
TIMESTAMP_RE = re.compile(r"^\d{14}$")
DECIMAL_RE = re.compile(r"^-?\d+\.\d+$")
INTEGER_RE = re.compile(r"^-?\d+$")
PERCENTILE_RE = re.compile(r"^(?:-?\d+(?:\.\d+)?%|[<>]\d+%)$")
WEEKS_DAYS_RE = re.compile(r"^\d+w \d+d$")


# -----------------------
# Dataclasses
# -----------------------


@dataclass
class Cluster:
    """One named cluster + its observer / viewpoint prefix lists."""

    name: str
    observer_prefixes: list[str] = field(default_factory=list)
    viewpoint_prefixes: list[str] = field(default_factory=list)


@dataclass
class ObserverField:
    """One Observer leaf, keyed by (path, single inherited label)."""

    path: str
    label: str = ""
    types: set[str] = field(default_factory=set)
    value_classes: set[str] = field(default_factory=set)
    samples: list[str] = field(default_factory=list)
    files: set[str] = field(default_factory=set)
    overflow: bool = False


@dataclass
class ViewpointField:
    """One HL7 OBX-3 primary identifier + its short/long labels."""

    identifier: str
    short_label: str = ""
    long_label: str = ""
    types: set[str] = field(default_factory=set)
    value_classes: set[str] = field(default_factory=set)
    obx_types: set[str] = field(default_factory=set)
    samples: list[str] = field(default_factory=list)
    files: set[str] = field(default_factory=set)
    overflow: bool = False


# -----------------------
# Cluster loading + matching
# -----------------------


def load_clusters(path: Path = CLUSTERS_YAML) -> list[Cluster]:
    """Parse clusters.yaml into a list of `Cluster` dataclasses."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must be a YAML list of cluster entries")
    out: list[Cluster] = []
    for entry in data:
        out.append(
            Cluster(
                name=entry["cluster"],
                observer_prefixes=list(entry.get("observer_prefixes", []) or []),
                viewpoint_prefixes=list(entry.get("viewpoint_prefixes", []) or []),
            )
        )
    return out


def classify_observer(path: str, clusters: list[Cluster]) -> str:
    """First cluster whose observer_prefixes contains a string prefix of `path`."""
    for cluster in clusters:
        if any(path.startswith(prefix) for prefix in cluster.observer_prefixes):
            return cluster.name
    return UNCLUSTERED


def classify_viewpoint(identifier: str, clusters: list[Cluster]) -> str:
    """First cluster whose viewpoint_prefixes contains a string prefix of `identifier`."""
    for cluster in clusters:
        if any(identifier.startswith(prefix) for prefix in cluster.viewpoint_prefixes):
            return cluster.name
    return UNCLUSTERED


# -----------------------
# Concept aliases
# -----------------------


def load_concept_aliases(
    path: Path = CONCEPT_ALIASES_YAML,
) -> tuple[dict[tuple[str, str], str], dict[str, str]]:
    """Parse concept_aliases.yaml into (observer, viewpoint) lookup tables.

    Returns a 2-tuple: the first dict maps `(observer_path, label)` to
    concept_key; the second maps OBX-3 identifier to concept_key. An
    Observer entry with no label gets `label=""`.
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a YAML mapping of concept -> entry")
    observer_lookup: dict[tuple[str, str], str] = {}
    viewpoint_lookup: dict[str, str] = {}
    for concept_key, entry in data.items():
        for obs in entry.get("observer") or []:
            key = (obs["path"], obs.get("label", "") or "")
            observer_lookup[key] = concept_key
        for vp in entry.get("viewpoint") or []:
            viewpoint_lookup[vp] = concept_key
    return observer_lookup, viewpoint_lookup


# -----------------------
# Type + value-class detection
# -----------------------


def json_type(value: Any) -> str:
    """Raw JSON shape token: null / bool / int / float / str."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    return "str"


def value_class(value: Any, path: str = "") -> str:  # noqa: C901
    """Semantic class with path-name hints (percentile, weeks_days, date, ...)."""
    if value is None or value == "":
        return "empty"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "decimal"
    text = str(value).strip()
    lower_path = path.lower()
    if PERCENTILE_RE.match(text) or "percentile" in lower_path:
        return "percentile"
    if WEEKS_DAYS_RE.match(text) or "gestationalage" in lower_path:
        return "weeks_days"
    if DATE_RE.match(text) or lower_path.endswith("date") or "date" in lower_path:
        return "date"
    if TIME_RE.match(text) or TIMESTAMP_RE.match(text) or "time" in lower_path:
        return "time"
    if DECIMAL_RE.match(text):
        return "decimal"
    if INTEGER_RE.match(text):
        return "integer"
    if len(text) > 80 or "\\.br\\" in text or "\n" in text:
        return "free_text"
    return "coded_text"


# -----------------------
# Observer walker (label-split)
# -----------------------


def _next_label(value: Any, current: str) -> str:
    """Pick up `label` field on a dict node; otherwise inherit `current`."""
    if isinstance(value, dict):
        lbl = value.get("label")
        if isinstance(lbl, (str, int, float)) and str(lbl):
            return str(lbl)
    return current


def add_sample(samples: list[str], value: str, record: Any) -> None:
    """Append `value` to `samples` (deduped, capped at SAMPLE_LIMIT, overflow flag)."""
    if value == "":
        return
    if value not in samples and len(samples) < SAMPLE_LIMIT:
        samples.append(value)
    elif value not in samples:
        record.overflow = True


def walk_observer(
    value: Any,
    path: str,
    file_name: str,
    fields: dict[tuple[str, str], ObserverField],
    label_ctx: str = "",
) -> None:
    """Recursive descent; one record per (path, inherited-label) at each leaf."""
    next_ctx = _next_label(value, label_ctx)
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{path}.{key}" if path else key
            walk_observer(value[key], child, file_name, fields, next_ctx)
        return
    if isinstance(value, list):
        child = f"{path}[]" if path else "[]"
        for item in value:
            walk_observer(item, child, file_name, fields, next_ctx)
        return

    if not path:
        return
    key = (path, label_ctx)
    record = fields.setdefault(key, ObserverField(path=path, label=label_ctx))
    record.types.add(json_type(value))
    record.value_classes.add(value_class(value, path))
    record.files.add(file_name)
    if value is not None:
        add_sample(record.samples, str(value), record)


# -----------------------
# HL7 walker
# -----------------------


def parse_obx_line(line: str) -> tuple[str, str, str, str, str] | None:
    """Pipe-split one OBX line into (type, identifier, short, long, value) or None."""
    if not line.startswith("OBX|"):
        return None
    parts = line.rstrip("\r\n").split("|")
    if len(parts) < 6:
        return None
    obx_type = parts[2]
    id_parts = parts[3].split("^")
    identifier = id_parts[0]
    short_label = id_parts[1] if len(id_parts) > 1 else ""
    long_label = id_parts[2] if len(id_parts) > 2 else ""
    return obx_type, identifier, short_label, long_label, parts[5]


def display_hl7_value(raw_value: str) -> str:
    """Render `primary (secondary)` when the second caret-segment differs."""
    if not raw_value:
        return ""
    parts = raw_value.split("^")
    if len(parts) >= 2 and parts[1] and parts[1] != parts[0]:
        return f"{parts[0]} ({parts[1]})"
    return parts[0]


def hl7_observed_type(raw_value: str, obx_type: str) -> str:
    """JSON-shape-equivalent token for an HL7 OBX-5 value."""
    primary = raw_value.split("^", 1)[0] if raw_value else ""
    if primary == "":
        return "null"
    if obx_type == "NM":
        return "float" if "." in primary else "int"
    return "str"


def hl7_value_class(raw_value: str, identifier: str, obx_type: str) -> str:
    """Semantic class for an HL7 OBX value with identifier + OBX-2 hints."""
    parts = [part for part in raw_value.split("^") if part]
    search = " ".join(parts)
    if (
        any(PERCENTILE_RE.match(part) for part in parts)
        or "percentile" in identifier.lower()
    ):
        return "percentile"
    if any(WEEKS_DAYS_RE.match(part) for part in parts):
        return "weeks_days"
    if obx_type == "DT":
        return "date"
    if obx_type == "TM":
        return "time"
    if obx_type == "TS":
        return "timestamp"
    if obx_type == "NM":
        return "decimal" if "." in search else "integer"
    return value_class(search, identifier)


def walk_hl7_file(path: Path, fields: dict[str, ViewpointField]) -> int:
    """Parse one HL7 file; return the count of OBX rows seen."""
    count = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parsed = parse_obx_line(line)
            if parsed is None:
                continue
            obx_type, identifier, short_label, long_label, raw_value = parsed
            record = fields.setdefault(
                identifier, ViewpointField(identifier=identifier)
            )
            record.short_label = record.short_label or short_label
            record.long_label = record.long_label or long_label
            record.obx_types.add(obx_type)
            record.types.add(hl7_observed_type(raw_value, obx_type))
            record.value_classes.add(hl7_value_class(raw_value, identifier, obx_type))
            record.files.add(path.name)
            add_sample(record.samples, display_hl7_value(raw_value), record)
            count += 1
    return count


# -----------------------
# Pairing
# -----------------------


def normalize_token(text: str) -> str:
    """Collapse a name into a lower-snake-case token for matching."""
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", text)
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).lower()
    return re.sub(r"_+", "_", text).strip("_")


def observer_match_tokens(record: ObserverField) -> set[str]:
    """Tokens from path leaf + inherited label (label always included if set)."""
    tokens = {normalize_token(record.path.rsplit(".", 1)[-1])}
    if record.label:
        tokens.add(normalize_token(record.label))
    return {t for t in tokens if t}


def viewpoint_match_tokens(record: ViewpointField) -> set[str]:
    """Tokens from identifier leaf + short_label + long_label."""
    pieces = [
        record.identifier.rsplit(".", 1)[-1],
        record.short_label,
        record.long_label,
    ]
    return {t for t in (normalize_token(p) for p in pieces) if t}


def compatible_classes(left: set[str], right: set[str]) -> bool:
    """Either a direct class overlap, or both sides have any numeric class."""
    if left & right:
        return True
    numeric = {"integer", "decimal", "percentile"}
    return bool(left & numeric and right & numeric)


def pair_fields(
    observers: list[ObserverField], viewpoints: list[ViewpointField]
) -> list[tuple[ObserverField | None, ViewpointField | None]]:
    """Greedy first-fit pairing keyed on token overlap + compatible value classes."""
    remaining = list(viewpoints)
    pairs: list[tuple[ObserverField | None, ViewpointField | None]] = []
    for observer in observers:
        observer_tokens = observer_match_tokens(observer)
        candidates: list[tuple[int, str, ViewpointField]] = []
        for viewpoint in remaining:
            shared = observer_tokens & viewpoint_match_tokens(viewpoint)
            if not shared:
                continue
            if not compatible_classes(observer.value_classes, viewpoint.value_classes):
                continue
            score = len(shared)
            if observer.label and normalize_token(observer.label) in shared:
                score += 3
            if normalize_token(observer.path.rsplit(".", 1)[-1]) in shared:
                score += 1
            candidates.append((score, viewpoint.identifier, viewpoint))
        if candidates:
            candidates.sort(key=lambda item: (-item[0], item[1]))
            match = candidates[0][2]
            remaining.remove(match)
            pairs.append((observer, match))
        else:
            pairs.append((observer, None))
    pairs.extend((None, viewpoint) for viewpoint in remaining)
    return pairs


# -----------------------
# Row formatting
# -----------------------


def joined(values: set[str]) -> str:
    """Pipe-join a set in deterministic sorted order."""
    return "|".join(sorted(values))


def sample_text(samples: list[str], overflow: bool) -> str:
    """Pipe-join samples, appending `|...` when capped."""
    text = "|".join(samples)
    return f"{text}|..." if overflow and text else text


def coverage(files: set[str], total: int) -> str:
    """Format file coverage as `present/total`."""
    return f"{len(files)}/{total}"


def viewpoint_type_signature(record: ViewpointField) -> str:
    """`observed (declared)` for HL7 cells; observed alone if no OBX-2 seen."""
    observed = joined(record.types)
    declared = joined(record.obx_types)
    return f"{observed} ({declared})" if declared else observed


# -----------------------
# Build + write
# -----------------------


def build_rows(
    observer_fields: dict[tuple[str, str], ObserverField],
    viewpoint_fields: dict[str, ViewpointField],
    clusters: list[Cluster],
    observer_total: int,
    viewpoint_total: int,
    observer_concepts: dict[tuple[str, str], str] | None = None,
    viewpoint_concepts: dict[str, str] | None = None,
) -> list[list[str]]:
    """Iterate clusters in YAML order; pair-match within each cluster; emit rows.

    When `observer_concepts` / `viewpoint_concepts` lookups are provided,
    each row's `concept_key` is populated from them (observer side wins;
    viewpoint-only rows pick up the viewpoint concept).
    """
    observer_concepts = observer_concepts or {}
    viewpoint_concepts = viewpoint_concepts or {}
    by_cluster_obs: dict[str, list[ObserverField]] = defaultdict(list)
    by_cluster_vp: dict[str, list[ViewpointField]] = defaultdict(list)
    cluster_names = [c.name for c in clusters] + [UNCLUSTERED]

    for record in observer_fields.values():
        by_cluster_obs[classify_observer(record.path, clusters)].append(record)
    for record in viewpoint_fields.values():
        by_cluster_vp[classify_viewpoint(record.identifier, clusters)].append(record)

    rows: list[list[str]] = []
    for cluster in cluster_names:
        obs_sorted = sorted(by_cluster_obs[cluster], key=lambda r: (r.path, r.label))
        vp_sorted = sorted(by_cluster_vp[cluster], key=lambda r: r.identifier)
        for obs, vp in pair_fields(obs_sorted, vp_sorted):
            obs_concept = (
                observer_concepts.get((obs.path, obs.label), "") if obs else ""
            )
            vp_concept = viewpoint_concepts.get(vp.identifier, "") if vp else ""
            concept_key = obs_concept or vp_concept
            rows.append(
                [
                    concept_key,
                    cluster,
                    obs.path if obs else "",
                    obs.label if obs else "",
                    joined(obs.types) if obs else "",
                    joined(obs.value_classes) if obs else "",
                    sample_text(obs.samples, obs.overflow) if obs else "",
                    coverage(obs.files, observer_total) if obs else "",
                    f"OBX {vp.identifier}" if vp else "",
                    vp.short_label if vp else "",
                    vp.long_label if vp else "",
                    viewpoint_type_signature(vp) if vp else "",
                    joined(vp.value_classes) if vp else "",
                    sample_text(vp.samples, vp.overflow) if vp else "",
                    coverage(vp.files, viewpoint_total) if vp else "",
                    "",
                ]
            )
    return rows


def main() -> None:
    """Walk both corpora, classify + pair, write comparison.csv."""
    clusters = load_clusters()
    observer_concepts, viewpoint_concepts = load_concept_aliases()
    logger.info(
        "Loaded concept aliases (%d Observer keys, %d HL7 keys)",
        len(observer_concepts),
        len(viewpoint_concepts),
    )
    observer_paths = sorted(OBSERVER_DIR.glob(OBSERVER_GLOB))
    hl7_paths = sorted(HL7_DIR.glob(HL7_GLOB))
    if not observer_paths:
        logger.error("No Observer JSONs at %s/%s", OBSERVER_DIR, OBSERVER_GLOB)
        raise SystemExit(1)
    if not hl7_paths:
        logger.error("No HL7 files at %s/%s", HL7_DIR, HL7_GLOB)
        raise SystemExit(1)

    observer_fields: dict[tuple[str, str], ObserverField] = {}
    for path in observer_paths:
        walk_observer(
            json.loads(path.read_text(encoding="utf-8")), "", path.name, observer_fields
        )
        logger.info("Walked Observer file %s", path.name)

    viewpoint_fields: dict[str, ViewpointField] = {}
    obx_count = 0
    for path in hl7_paths:
        obx_count += walk_hl7_file(path, viewpoint_fields)
        logger.info("Walked HL7 file %s", path.name)

    rows = build_rows(
        observer_fields,
        viewpoint_fields,
        clusters,
        len(observer_paths),
        len(hl7_paths),
        observer_concepts,
        viewpoint_concepts,
    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_COLUMNS)
        writer.writerows(rows)

    cluster_counts: dict[str, int] = defaultdict(int)
    concept_tagged = 0
    paired = 0
    for row in rows:
        cluster_counts[row[1]] += 1
        if row[0]:
            concept_tagged += 1
        if row[2] and row[8]:
            paired += 1

    logger.info("\n=== Parse Summary ===")
    logger.info("Observer files     : %d", len(observer_paths))
    logger.info("HL7 files          : %d", len(hl7_paths))
    logger.info("OBX rows parsed    : %d", obx_count)
    logger.info("Observer records   : %d", len(observer_fields))
    logger.info("HL7 identifiers    : %d", len(viewpoint_fields))
    logger.info("Rows written       : %d", len(rows))
    logger.info("Paired cross-source: %d", paired)
    logger.info("Concept-tagged rows: %d", concept_tagged)
    logger.info("Output             : %s", OUT_CSV)
    logger.info("\n=== Cluster Counts ===")
    for cluster in sorted(cluster_counts):
        logger.info("  %-25s : %d", cluster, cluster_counts[cluster])


if __name__ == "__main__":
    main()
