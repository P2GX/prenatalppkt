"""
render_readme.py

Read `docs/data_dictionary/comparison.csv` and emit the matching
`docs/data_dictionary/README.md`. One section per cluster (in
YAML-curated clinical reading order), each with a single paired
Observer + EVMS GE HL7 table.

The README is fully generated; edit `render_readme.py`,
`extract_all.py`, or `clusters.yaml`, never the README itself.
"""

from __future__ import annotations

import logging
from pathlib import Path

from prenatalppkt.scripts.data_dict.render.clinician import render_clinician_overview
from prenatalppkt.scripts.data_dict.render.constants import CLUSTER_NOTES
from prenatalppkt.scripts.data_dict.render.io import (
    group_by_cluster,
    load_cluster_order,
    load_rows,
)
from prenatalppkt.scripts.data_dict.render.pairing import render_pairing_section
from prenatalppkt.scripts.data_dict.render.tables import render_table

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

SCRIPT_DIR = Path(__file__).resolve().parent
PPKT_ROOT = SCRIPT_DIR.parents[3]
IN_CSV = PPKT_ROOT / "docs" / "data_dictionary" / "comparison.csv"
OUT_MD = PPKT_ROOT / "docs" / "data_dictionary" / "README.md"
CLUSTERS_YAML = SCRIPT_DIR / "clusters.yaml"
CONCEPT_ALIASES_YAML = SCRIPT_DIR / "concept_aliases.yaml"


def render(rows: list[dict[str, str]], cluster_order: list[str]) -> str:
    """Build the full README content as one Markdown string."""
    grouped = group_by_cluster(rows)
    total_rows = len(rows)
    obs_rows = sum(1 for r in rows if r["observer_path"])
    vp_rows = sum(1 for r in rows if r["viewpoint_path"])
    paired = sum(1 for r in rows if r["observer_path"] and r["viewpoint_path"])

    lines: list[str] = []
    lines.append("# prenatalppkt data dictionary")
    lines.append("")
    lines.append(
        "Cross-source field inventory for the prenatalppkt ETL. Every "
        "leaf path in the CUIMC Observer JSON corpus and every OBX-3 "
        "identifier in the EVMS GE HL7 v2.4 corpus appears here, "
        "grouped into clinical clusters, with Observer rows split per "
        "measurement label and Observer + HL7 fields paired on the "
        "same row whenever a label token and value class match."
    )
    lines.append("")
    lines.append(
        f"`{IN_CSV.relative_to(PPKT_ROOT)}` is the canonical artifact "
        f"({total_rows} rows: {obs_rows} carry an Observer field, "
        f"{vp_rows} carry an HL7 field, {paired} pair both on one "
        "row). This README is generated from it; edit "
        "`render_readme.py`, `extract_all.py`, or `clusters.yaml`, "
        "never this file."
    )
    lines.append("")
    lines.extend(render_clinician_overview(rows, cluster_order, CONCEPT_ALIASES_YAML))
    lines.append("## Regenerate")
    lines.append("")
    lines.append("```bash")
    lines.append("uv run python src/prenatalppkt/scripts/data_dict/extract_all.py")
    lines.append("uv run python src/prenatalppkt/scripts/data_dict/render_readme.py")
    lines.append("```")
    lines.append("")
    lines.append("## Schema")
    lines.append("")
    lines.append(
        "Each CSV row is one Observer leaf (optionally with a single "
        "inherited measurement label), one HL7 OBX-3 identifier, or "
        "both when pairing fires. The 16 columns:"
    )
    lines.append("")
    lines.append(
        "`concept_key` (clinical concept this row maps to, populated "
        "from `concept_aliases.yaml`; empty when no concept matches), "
        "`cluster`, `observer_path`, `observer_label_values`, "
        "`observer_type`, `observer_value_class`, `observer_sample`, "
        "`observer_n_files`, `viewpoint_path`, "
        "`viewpoint_short_label`, `viewpoint_long_label`, "
        "`viewpoint_type`, `viewpoint_value_class`, "
        "`viewpoint_sample`, `viewpoint_n_files`, `notes`."
    )
    lines.append("")
    lines.append("## Value-class tokens")
    lines.append("")
    lines.append(
        "`empty`, `boolean`, `integer`, `decimal`, `percentile` "
        "(e.g. `56%`, `<5%`), `weeks_days` (e.g. `20w 3d`), `date`, "
        "`time`, `timestamp`, `coded_text` (short clinical "
        "enumeration), `free_text` (long-form narrative). HL7 "
        "viewpoint cells render sample values as `primary (display)` "
        "when the second OBX-5 caret-segment carries unit context "
        "(e.g. `163 (23w 2d)`, `45 (45%)`, `-0.9 (-0.9SD)`)."
    )
    lines.append("")
    lines.extend(render_pairing_section(rows, cluster_order))
    lines.append("## Clusters")
    lines.append("")

    for cluster in [*cluster_order, "_unclustered"]:
        cluster_rows = grouped.get(cluster)
        if not cluster_rows:
            continue
        lines.append(f"### {cluster}")
        lines.append("")
        note = CLUSTER_NOTES.get(cluster)
        if note:
            lines.append(note)
            lines.append("")
        obs_n = sum(1 for r in cluster_rows if r["observer_path"])
        vp_n = sum(1 for r in cluster_rows if r["viewpoint_path"])
        pair_n = sum(
            1 for r in cluster_rows if r["observer_path"] and r["viewpoint_path"]
        )
        lines.append(
            f"_{len(cluster_rows)} rows: {obs_n} Observer, "
            f"{vp_n} HL7, {pair_n} paired._"
        )
        lines.append("")
        lines.append(f"<!-- BEGIN: generated cluster={cluster} -->")
        lines.extend(render_table(cluster_rows))
        lines.append(f"<!-- END: generated cluster={cluster} -->")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    """Read the CSV, render the README, write it next to the CSV."""
    if not IN_CSV.exists():
        logger.error("Missing %s; run extract_all.py first", IN_CSV)
        raise SystemExit(1)
    rows = load_rows(IN_CSV)
    cluster_order = load_cluster_order(CLUSTERS_YAML)
    OUT_MD.write_text(render(rows, cluster_order), encoding="utf-8")
    logger.info("Wrote %s (%d rows ingested)", OUT_MD, len(rows))


if __name__ == "__main__":
    main()
