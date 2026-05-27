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

import csv
import logging
from collections import OrderedDict
from pathlib import Path

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
IN_CSV = PPKT_ROOT / "docs" / "data_dictionary" / "comparison.csv"
OUT_MD = PPKT_ROOT / "docs" / "data_dictionary" / "README.md"
CLUSTERS_YAML = SCRIPT_DIR / "clusters.yaml"


# -----------------------
# Per-cluster notes
# -----------------------

CLUSTER_NOTES: dict[str, str] = {
    "biometry": (
        "Fetal biometric measurements (HC, BPD, AC, FL, etc.), growth "
        "ratios, EFW values, first-trimester measurements (CRL, NT), "
        "and the GE FGR data block. Observer rows split by measurement "
        "label so each (BPD, AC, HC, ...) gets its own row."
    ),
    "anatomy_brain": "Fetal brain anatomy: ventricles, cerebellum, choroid plexus, posterior fossa.",
    "anatomy_face_neck": "Fetal face and neck anatomy: orbits, lips, palate, profile, neck.",
    "anatomy_chest_gi": "Fetal chest (non-cardiac) and gastrointestinal anatomy.",
    "anatomy_spine": "Fetal spine anatomy.",
    "anatomy_urinary": "Fetal genitourinary anatomy: kidneys, bladder, ureters.",
    "anatomy_general": (
        "System-agnostic anatomy wrapper fields (main / detail / "
        "anomalies metadata) that apply across organ systems."
    ),
    "cardiac": (
        "Fetal cardiac anatomy and echocardiography measurements; "
        "heart-specific findings on both sides."
    ),
    "amniotic_fluid": (
        "Amniotic fluid index, single deepest pocket, and the GE "
        "amniotic-fluid measurement family."
    ),
    "placenta_cord": (
        "Placenta location and grading, umbilical cord findings, "
        "umbilical artery Doppler indices, and fetal-vessel data."
    ),
    "fetal_procedures": (
        "Invasive fetal procedures: amniocentesis, FBS/CVS, ectopic "
        "pregnancy management, other procedures."
    ),
    "fetus_core": (
        "Per-fetus identity (number, position, presentation, tone, "
        "activity), antepartum testing (NST, BPP)."
    ),
    "indication_impression": (
        "Free-text and coded exam indications, ICD-10 codes, and narrative impressions."
    ),
    "dating": ("Pregnancy dating: LMP, EDD, gestational age, agreed dating method."),
    "encounter": (
        "Exam-level metadata: date, location, signing, exam type, "
        "referring provider, accession, plus GE imaging-parameter "
        "and structured-report file blocks."
    ),
    "maternal_subject": (
        "Maternal demographics and history: patient block, "
        "obstetric history, family/anamnestic history, antenatal "
        "booking, screening tests."
    ),
    "non_fetal_gyn": (
        "Non-fetal gynecologic anatomy: adnexa, cervix, "
        "endomyometrial / uterine findings, uterine artery Doppler, "
        "gynecologic procedures."
    ),
    "_unclustered": (
        "Paths and identifiers that matched no cluster prefix. "
        "Expected to be empty; non-empty means clusters.yaml needs a new prefix."
    ),
}


# -----------------------
# Table layout
# -----------------------

TABLE_COLUMNS = [
    "observer_path",
    "observer_label_values",
    "observer_value_class",
    "observer_sample",
    "viewpoint_path",
    "viewpoint_short_label",
    "viewpoint_value_class",
    "viewpoint_sample",
    "notes",
]


# -----------------------
# Helpers
# -----------------------


def escape_cell(value: str) -> str:
    """Escape characters that would otherwise break a Markdown table cell."""
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def load_cluster_order(path: Path = CLUSTERS_YAML) -> list[str]:
    """YAML-declared cluster names in the order the README should render them."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [entry["cluster"] for entry in data]


def load_rows(path: Path = IN_CSV) -> list[dict[str, str]]:
    """Read comparison.csv into a list of row dicts."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def group_by_cluster(
    rows: list[dict[str, str]],
) -> OrderedDict[str, list[dict[str, str]]]:
    """Group rows by cluster, preserving insertion order from the CSV."""
    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in rows:
        grouped.setdefault(row["cluster"], []).append(row)
    return grouped


def render_table(rows: list[dict[str, str]]) -> list[str]:
    """Markdown lines for one cluster's paired table (no row cap)."""
    lines = [
        "| " + " | ".join(TABLE_COLUMNS) + " |",
        "| " + " | ".join("---" for _ in TABLE_COLUMNS) + " |",
    ]
    for row in rows:
        lines.append(
            "| " + " | ".join(escape_cell(row[c]) for c in TABLE_COLUMNS) + " |"
        )
    return lines


# -----------------------
# Render
# -----------------------


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
        "both when pairing fires. The 15 columns:"
    )
    lines.append("")
    lines.append(
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
    rows = load_rows()
    cluster_order = load_cluster_order()
    OUT_MD.write_text(render(rows, cluster_order), encoding="utf-8")
    logger.info("Wrote %s (%d rows ingested)", OUT_MD, len(rows))


if __name__ == "__main__":
    main()
