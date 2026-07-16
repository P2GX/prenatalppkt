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

    When the external prenatal-site-data checkout isn't present, falls
    back to this repo's own synthetic fixtures under tests/data/ and
    writes to `.local` suffixed output files instead (see paths.py) -
    never overwrites the real corpus-derived comparison.csv.

Output:
    prenatalppkt/docs/data_dictionary/comparison.csv (16 columns;
    the first column is `concept_key`, populated by looking up each
    row against `concept_aliases.yaml`).
"""

from __future__ import annotations

import csv
import json
import logging
from collections import defaultdict

from prenatalppkt.scripts.data_dict.extract.build import build_rows
from prenatalppkt.scripts.data_dict.extract.clusters import load_clusters
from prenatalppkt.scripts.data_dict.extract.concept_aliases import load_concept_aliases
from prenatalppkt.scripts.data_dict.extract.hl7 import walk_hl7_file
from prenatalppkt.scripts.data_dict.extract.models import ObserverField, ViewpointField
from prenatalppkt.scripts.data_dict.extract.observer import walk_observer
from prenatalppkt.scripts.data_dict.paths import (
    HL7_DIR,
    HL7_GLOBS,
    OBSERVER_DIR,
    OBSERVER_GLOB,
    OUT_CSV,
    SCRIPT_DIR,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

CLUSTERS_YAML = SCRIPT_DIR / "clusters.yaml"
CONCEPT_ALIASES_YAML = SCRIPT_DIR / "concept_aliases.yaml"

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


def main() -> None:
    """Walk both corpora, classify + pair, write comparison.csv."""
    clusters = load_clusters(CLUSTERS_YAML)
    observer_concepts, viewpoint_concepts = load_concept_aliases(CONCEPT_ALIASES_YAML)
    logger.info(
        "Loaded concept aliases (%d Observer keys, %d HL7 keys)",
        len(observer_concepts),
        len(viewpoint_concepts),
    )
    observer_paths = sorted(OBSERVER_DIR.glob(OBSERVER_GLOB))
    hl7_paths = sorted({p for pattern in HL7_GLOBS for p in HL7_DIR.glob(pattern)})
    if not observer_paths:
        logger.error("No Observer JSONs at %s/%s", OBSERVER_DIR, OBSERVER_GLOB)
        raise SystemExit(1)
    if not hl7_paths:
        logger.error("No HL7 files at %s/%s", HL7_DIR, HL7_GLOBS)
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
