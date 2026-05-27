"""
render_readme.py

Read `docs/data_dictionary/comparison.csv` and emit the matching
`docs/data_dictionary/README.md`. The README has one section per
cluster, each with two tables (Observer leaf paths and EVMS GE HL7
OBX identifiers) so a reader can scan both corpora side by side
without opening the CSV.

The README is fully generated; edit `render_readme.py` or
`clusters.yaml`, never the README itself.
"""

from __future__ import annotations

import csv
import logging
from collections import defaultdict
from pathlib import Path

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


# -----------------------
# Cluster descriptions
# -----------------------

CLUSTER_NOTES: dict[str, str] = {
    "biometry": (
        "Fetal biometric measurements (HC, BPD, AC, FL, etc.), growth "
        "ratios, EFW values, first-trimester measurements (CRL, NT), "
        "and the GE FGR data block."
    ),
    "cardiac": (
        "Fetal cardiac anatomy and echocardiography measurements; "
        "heart-specific findings on both sides."
    ),
    "anatomy": (
        "Fetal organ-system anatomy: brain, face, GI tract, chest, "
        "spine, urinary tract, plus the Observer per-system anatomy "
        "array."
    ),
    "amniotic_fluid": (
        "Amniotic fluid index, single deepest pocket, and the GE "
        "amniotic-fluid measurement family."
    ),
    "placenta_cord": (
        "Placenta location and grading, umbilical cord findings, "
        "umbilical artery Doppler indices, and fetal-vessel data."
    ),
    "fetus_core": (
        "Per-fetus identity (number, position, presentation, tone, "
        "activity), antepartum testing (NST, BPP), and invasive "
        "procedures (amniocentesis, FBS/CVS)."
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
}


# -----------------------
# Loading
# -----------------------


def load_rows(path: Path) -> list[dict[str, str]]:
    """Read comparison.csv into a list of row dicts."""
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def split_by_cluster(
    rows: list[dict[str, str]],
) -> dict[str, dict[str, list[dict[str, str]]]]:
    """Group rows by cluster, then by side (obs vs vp)."""
    grouped: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(
        lambda: {"obs": [], "vp": []}
    )
    for row in rows:
        side = "obs" if row["observer_path"] else "vp"
        grouped[row["cluster"]][side].append(row)
    return grouped


# -----------------------
# Rendering
# -----------------------


def md_escape(text: str) -> str:
    """Escape `|` and backticks so they don't break a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def format_cell(text: str) -> str:
    """Wrap a cell value in backticks when non-empty, return em-dash otherwise."""
    if not text:
        return "-"
    return f"`{md_escape(text)}`"


def render_observer_table(rows: list[dict[str, str]]) -> list[str]:
    """Return Markdown lines for the Observer sub-table of one cluster."""
    if not rows:
        return ["_No Observer paths in this cluster._", ""]
    lines = ["| observer_path | type | sample | files |", "| --- | --- | --- | --- |"]
    rows_sorted = sorted(rows, key=lambda r: r["observer_path"])
    for r in rows_sorted:
        lines.append(
            f"| {format_cell(r['observer_path'])} "
            f"| {format_cell(r['observer_type'])} "
            f"| {format_cell(r['observer_sample'])} "
            f"| {r['observer_n_files']} |"
        )
    lines.append("")
    return lines


def render_viewpoint_table(rows: list[dict[str, str]]) -> list[str]:
    """Return Markdown lines for the HL7 (viewpoint) sub-table of one cluster."""
    if not rows:
        return ["_No EVMS GE HL7 identifiers in this cluster._", ""]
    lines = ["| viewpoint_path | type | sample | files |", "| --- | --- | --- | --- |"]
    rows_sorted = sorted(rows, key=lambda r: r["viewpoint_path"])
    for r in rows_sorted:
        lines.append(
            f"| {format_cell(r['viewpoint_path'])} "
            f"| {format_cell(r['viewpoint_type'])} "
            f"| {format_cell(r['viewpoint_sample'])} "
            f"| {r['viewpoint_n_files']} |"
        )
    lines.append("")
    return lines


def render(rows: list[dict[str, str]]) -> str:
    """Build the full README content as one Markdown string."""
    grouped = split_by_cluster(rows)
    total_rows = len(rows)
    obs_paths = sum(1 for r in rows if r["observer_path"])
    vp_paths = total_rows - obs_paths

    lines: list[str] = []
    lines.append("# prenatalppkt data dictionary")
    lines.append("")
    lines.append(
        "Cross-source field inventory for the prenatalppkt ETL: every "
        "leaf path in the CUIMC Observer JSON corpus and every OBX-3 "
        "identifier in the EVMS GE HL7 v2.4 corpus, grouped into a "
        "small set of clinical clusters so reviewers can compare the "
        "two surfaces side by side."
    )
    lines.append("")
    lines.append(
        f"`{IN_CSV.relative_to(PPKT_ROOT)}` is the canonical artifact "
        f"({total_rows} rows: {obs_paths} Observer paths, "
        f"{vp_paths} HL7 identifiers). This README is generated from "
        "it; edit `render_readme.py` or `clusters.yaml`, not this "
        "file."
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
        "Each row in `comparison.csv` is either an Observer leaf "
        "path or an HL7 OBX-3 identifier (never both). The 10 "
        "columns:"
    )
    lines.append("")
    lines.append(
        "`cluster`, `observer_path`, `observer_type`, "
        "`observer_sample`, `observer_n_files`, `viewpoint_path`, "
        "`viewpoint_type`, `viewpoint_sample`, `viewpoint_n_files`, "
        "`notes`."
    )
    lines.append("")
    lines.append("## Type tokens")
    lines.append("")
    lines.append(
        "`null`, `bool`, `int`, `float`, `str`, `list`, `dict`, "
        "`percentile_str` (e.g. `45%`, `<5%`), `weeks_days_str` "
        "(e.g. `20w 3d`). HL7 viewpoint cells append the declared "
        "OBX-2 type in parens (`ST`, `NM`, `DT`, `TM`, `TS`)."
    )
    lines.append("")
    lines.append("## Clusters")
    lines.append("")

    for cluster in sorted(grouped):
        sides = grouped[cluster]
        lines.append(f"### {cluster}")
        lines.append("")
        note = CLUSTER_NOTES.get(cluster)
        if note:
            lines.append(note)
            lines.append("")
        lines.append(
            f"_{len(sides['obs'])} Observer paths, {len(sides['vp'])} HL7 identifiers._"
        )
        lines.append("")
        lines.append("#### Observer (CUIMC JSON)")
        lines.append("")
        lines.extend(render_observer_table(sides["obs"]))
        lines.append("#### EVMS GE HL7")
        lines.append("")
        lines.extend(render_viewpoint_table(sides["vp"]))

    return "\n".join(lines) + "\n"


# -----------------------
# Main
# -----------------------


def main() -> None:
    """Read the CSV, render the README, write it next to the CSV."""
    if not IN_CSV.exists():
        logger.error("Missing %s; run extract_all.py first", IN_CSV)
        raise SystemExit(1)
    rows = load_rows(IN_CSV)
    OUT_MD.write_text(render(rows))
    logger.info("Wrote %s (%d rows ingested)", OUT_MD, len(rows))


if __name__ == "__main__":
    main()
