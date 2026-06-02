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

VALUE_CLASS_LABEL: dict[str, str] = {
    "decimal": "number",
    "integer": "number",
    "percentile": "percentile",
    "coded_text": "coded",
    "free_text": "free text",
    "weeks_days": "weeks+days",
    "date": "date",
    "time": "time",
    "timestamp": "timestamp",
    "boolean": "yes/no",
    "empty": "",
}


CLUSTER_TEMPLATE_GUIDANCE: dict[str, str] = {
    "biometry": (
        "Both systems capture the core biometry suite (BPD, AC, HC, CRL, "
        "Femur, Humerus, Nuchal Fold) as numbers in mm. ViewPoint reports "
        "one HL7 field per measurement; Observer stores them as a list "
        "tagged by `label`. The XLSX should have one row per measurement "
        "with a number column for the raw value and a percentile column."
    ),
    "anatomy_brain": (
        "ViewPoint has a discrete `BrainFetus.*` HL7 namespace (ventricles, "
        "cerebellum, choroid plexus, posterior fossa). Observer captures the "
        "same findings inside free-text `fetuses[].anatomy[].*.brain` fields. "
        "The XLSX should pre-define brain anatomy fields so the receiving "
        "center isn't forced to free-type them."
    ),
    "anatomy_face_neck": (
        "ViewPoint has `FaceFetus.*`; Observer keeps these as free-text "
        "anatomy entries. Pre-define orbits, lips, palate, profile, neck "
        "fields in the XLSX."
    ),
    "anatomy_chest_gi": (
        "ViewPoint splits chest (non-cardiac) and GI into discrete fields; "
        "Observer lumps them into anatomy free text. Pre-define discrete "
        "chest + GI anatomy fields in the XLSX."
    ),
    "anatomy_spine": (
        "ViewPoint has `SpineFetus.*`; Observer keeps spine findings under "
        "free-text anatomy. The XLSX should pre-define spine fields."
    ),
    "anatomy_urinary": (
        "ViewPoint has `UrinaryTractFetus.*` (kidneys, bladder, ureters); "
        "Observer mostly free-text. Pre-define the urinary fields in the XLSX."
    ),
    "anatomy_general": (
        "Observer-only structural anatomy wrappers. ViewPoint has no "
        "equivalent namespace. The XLSX should provide a wide free-text "
        "column for system-agnostic anatomy notes."
    ),
    "cardiac": (
        "Both systems carry detailed cardiac findings and echocardiography "
        "measurements. The XLSX should accommodate both discrete "
        "cardiac-anatomy fields and free-text echocardiography findings."
    ),
    "amniotic_fluid": (
        "Both systems carry amniotic-fluid index and deepest-pocket. "
        "Numbers in cm. The XLSX should have AFI and SDP numeric columns "
        "plus a categorical (oligo / normal / polyhydramnios)."
    ),
    "placenta_cord": (
        "Both systems cover placenta + cord findings but tokenize "
        "differently (Observer's `cord.numberOfVessels` vs ViewPoint's "
        "`Cord.VesselCount`). The XLSX should include both naming styles "
        "as alias columns until a concept alias is hand-curated."
    ),
    "fetal_procedures": (
        "Observer-only invasive procedures (amniocentesis, CVS/FBS, "
        "ectopic mgmt). The XLSX should provide a procedure-type column "
        "plus a free-text findings column."
    ),
    "fetus_core": (
        "Both systems carry per-fetus identity (fetal sex, presentation, "
        "movements, tone). Fetal sex maps directly to a coded enum. The "
        "XLSX should have one row per fetus with these as columns."
    ),
    "indication_impression": (
        "Both systems carry ICD-10 indication codes + descriptions. Coded "
        "in both. The XLSX should have an indication-code column "
        "(ICD-10 format) and a free-text impression column."
    ),
    "dating": (
        "Both systems carry pregnancy dating: LMP, EDD, gestational age, "
        "agreed dating string. They tokenize differently (Observer's "
        "`ga_by_dates` vs ViewPoint's `ExamOBDating.*`). The XLSX should "
        "have LMP, EDD, GA-at-exam, and dating-method columns."
    ),
    "encounter": (
        "Exam-level metadata: date, location, signing, exam type, referring "
        "provider, accession. ViewPoint has structured `Exam.*` + "
        "`ExamAddData.*`; Observer scatters this under `exam.*` keys. The "
        "XLSX should pre-define encounter metadata as a header block."
    ),
    "maternal_subject": (
        "Both systems carry maternal demographics + obstetric history "
        "(gravida, para, name, age). Coded in both. The XLSX should have a "
        "maternal header block with these as standard columns."
    ),
    "non_fetal_gyn": (
        "Mostly Observer-only gynecologic findings (adnexa, cervix, "
        "uterine artery, gyn procedures). Cervix funneling is the one "
        "concept paired across sources. The XLSX should provide a "
        "free-text gyn-findings block plus discrete cervix-length / "
        "funneling columns."
    ),
    "_unclustered": (
        "Should stay empty. If a row lands here, clusters.yaml needs a new prefix."
    ),
}


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
    "concept_key",
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


def _clinician_type(value_class: str) -> str:
    """Map a `value_class` token to a clinician-friendly type label."""
    if not value_class:
        return ""
    parts = [VALUE_CLASS_LABEL.get(tok, tok) for tok in value_class.split("|")]
    return "/".join(sorted({p for p in parts if p}))


def _first_row_for_concept(
    rows: list[dict[str, str]], concept_key: str
) -> dict[str, str] | None:
    """Return the first row whose concept_key matches, or None."""
    for row in rows:
        if row.get("concept_key") == concept_key:
            return row
    return None


def _short_description(concept_key: str, entry: dict[str, str]) -> str:
    """Pick the alias entry's description, fall back to the concept_key tail."""
    desc = (entry or {}).get("description", "").strip()
    return desc if desc else concept_key.rsplit(".", 1)[-1].replace("_", " ")


def _clinical_area(concept_key: str) -> str:
    """The clinical area is the leading dot-segment of the concept_key."""
    return concept_key.split(".", 1)[0]


def render_clinician_overview(
    rows: list[dict[str, str]], cluster_order: list[str], aliases_path: Path
) -> list[str]:
    """Render the plain-language cross-source field map aimed at clinicians.

    Inputs: the same CSV rows + cluster order that drive the cluster
    tables, plus a path to `concept_aliases.yaml` for descriptions.
    Output: markdown lines ready to splice into the README.
    """
    raw_aliases = yaml.safe_load(aliases_path.read_text(encoding="utf-8")) or {}

    lines: list[str] = ["## For clinicians: cross-source field map", ""]
    lines.append(
        "This section is a plain-language map of the data this pipeline "
        "ingests. It is meant for clinicians designing a "
        "[RIFGC-style XLSX template](../../../cerebro/docs/plans/01-rifgc-phenoxtract-style-refactor-python.md) "
        "for other prenatal-imaging centers to collect data through. "
        "The technical schema starts at `## Regenerate` below; you can "
        "stop reading after this section if you only need the field-level "
        "vocabulary."
    )
    lines.append("")

    lines.append("### What the two sources are")
    lines.append("")
    lines.append(
        "**Observer JSON** (CUIMC). A structured per-exam record exported "
        "by Columbia's prenatal-imaging system. Organized by fetus, with "
        "measurements, anatomy findings, and impressions stored as nested "
        "fields inside a single JSON file per exam. Strong on free-text "
        "narrative and multi-fetus structure; weaker on standardized "
        "HL7 codes."
    )
    lines.append("")
    lines.append(
        "**ViewPoint HL7** (EVMS, via GE). An HL7 v2.4 message stream "
        "exported from EVMS's GE ViewPoint system. Each finding is one "
        "OBX line with a system-specific field identifier (e.g. "
        "`SkullFetus.BiparietalDiameter`), a short label (e.g. `BPD`), "
        "and a value. Strong on standardized field naming; weaker on "
        "multi-fetus disambiguation and on free-text narrative."
    )
    lines.append("")
    lines.append(
        "The data dictionary below is built by walking both sources "
        "exhaustively and matching fields that hold the same clinical "
        "concept. `concept_aliases.yaml` lists the hand-curated matches; "
        f"the current alias file declares {len(raw_aliases)} concepts."
    )
    lines.append("")

    lines.append("### Concepts both systems capture (or only one side does)")
    lines.append("")
    lines.append(
        "The 22 concepts in `concept_aliases.yaml`, sorted by clinical "
        "area. `(Observer-only)` and `(ViewPoint-only)` mark concepts "
        "where only one source has the field; these are the ones the "
        "XLSX template will need to either collect by hand or infer at "
        "ETL time."
    )
    lines.append("")
    lines.append(
        "| Concept | Clinical area | Observer field | ViewPoint field | Type | Example |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for concept_key in sorted(raw_aliases):
        entry = raw_aliases[concept_key] or {}
        area = _clinical_area(concept_key)
        desc = _short_description(concept_key, entry)
        obs_entries = entry.get("observer") or []
        vp_entries = entry.get("viewpoint") or []
        obs_cell = "(ViewPoint-only)"
        if obs_entries:
            o = obs_entries[0]
            path = o.get("path", "")
            label = o.get("label", "") or ""
            obs_cell = f"`{path} @ {label}`" if label else f"`{path}`"
        vp_cell = f"`{vp_entries[0]}`" if vp_entries else "(Observer-only)"
        row = _first_row_for_concept(rows, concept_key)
        if row:
            type_label = _clinician_type(
                row.get("observer_value_class")
                or row.get("viewpoint_value_class")
                or ""
            )
            sample_src = row.get("observer_sample") or row.get("viewpoint_sample") or ""
            example = sample_src.split("|", 1)[0] if sample_src else ""
        else:
            type_label = ""
            example = ""
        lines.append(
            "| "
            + " | ".join(
                escape_cell(cell)
                for cell in (desc, area, obs_cell, vp_cell, type_label, example)
            )
            + " |"
        )
    lines.append("")

    lines.append("### Where the two sources diverge (by clinical area)")
    lines.append("")
    lines.append(
        "For each clinical area, how many fields each source has and what "
        "that means for an XLSX template. `Observer-only` counts include "
        "rows where Observer has data but no HL7 counterpart fired; "
        "`ViewPoint-only` is the converse. `Paired` is the count where "
        "both sides land on the same row."
    )
    lines.append("")
    lines.append(
        "| Clinical area | Observer-only | ViewPoint-only | Paired | What this means for the XLSX |"
    )
    lines.append("| --- | --- | --- | --- | --- |")
    for cluster in [*cluster_order, "_unclustered"]:
        cluster_rows = [r for r in rows if r["cluster"] == cluster]
        if not cluster_rows:
            continue
        obs_only = sum(
            1 for r in cluster_rows if r["observer_path"] and not r["viewpoint_path"]
        )
        vp_only = sum(
            1 for r in cluster_rows if r["viewpoint_path"] and not r["observer_path"]
        )
        paired = sum(
            1 for r in cluster_rows if r["observer_path"] and r["viewpoint_path"]
        )
        guidance = CLUSTER_TEMPLATE_GUIDANCE.get(cluster, "")
        lines.append(
            "| "
            + " | ".join(
                escape_cell(str(c))
                for c in (cluster, obs_only, vp_only, paired, guidance)
            )
            + " |"
        )
    lines.append("")

    lines.append("### Designing an RIFGC-style XLSX template from this dictionary")
    lines.append("")
    lines.append(
        "- **One row per `concept_key`.** Each row of `concept_aliases.yaml` "
        "is one entry in the XLSX. The `concept_key` (e.g. "
        "`biometry.bpd.measurement_mm`) is a stable identifier across "
        "template versions; the human-readable description goes in the "
        "next column over."
    )
    lines.append(
        "- **Seed columns from the concepts that already pair.** The "
        f"{len(raw_aliases)} concepts in the table above are the safest "
        "seed because both source systems already capture them. An XLSX "
        "collecting them will accept data from both CUIMC-style and "
        "EVMS-style centers without ETL-side guesswork."
    )
    lines.append(
        "- **Add a `source coverage` column** marking each row as "
        "`both`, `observer-only`, or `viewpoint-only`. This tells the "
        "receiving center which fields their existing system already "
        "produces vs which need manual entry."
    )
    lines.append(
        "- **Drive cell format from the type column** (number, "
        "percentile, coded, free text, weeks+days). Numeric cells should "
        "be unformatted; percentile cells should accept `45%` or `0.45`; "
        "free-text cells should be wide-column."
    )
    lines.append(
        "- **The XLSX is upstream of the ETL.** Once it exists, the "
        "PhenoXtract-style YAML config (see Plan 01) wraps it back into "
        "Phenopackets via the same data dictionary you're reading now."
    )
    lines.append("")
    return lines


def render_pairing_section(
    rows: list[dict[str, str]], cluster_order: list[str]
) -> list[str]:
    """Methodology blurb + per-cluster paired counts + biometry pairings table."""
    paired_by_cluster: dict[str, int] = {}
    for row in rows:
        if row["observer_path"] and row["viewpoint_path"]:
            paired_by_cluster[row["cluster"]] = (
                paired_by_cluster.get(row["cluster"], 0) + 1
            )
    total_paired = sum(paired_by_cluster.values())

    biometry_pairs = [
        row
        for row in rows
        if row["cluster"] == "biometry"
        and row["observer_path"]
        and row["viewpoint_path"]
    ]

    lines = ["## Pairing", ""]
    lines.append(
        "Pairing happens within each cluster, greedy first-fit. For each "
        "Observer record (one `(path, inherited-label)` tuple) the matcher "
        "builds a token set from the path leaf + the inherited measurement "
        "label; for each HL7 identifier it builds a token set from the "
        "identifier leaf + the OBX-3 short label + the OBX-3 long label. "
        "Tokens are matched case-insensitive after CamelCase / punctuation "
        "normalization. A pair fires when (a) at least one token overlaps "
        "and (b) value classes are compatible (direct overlap, or both sides "
        "are in the numeric family `{integer, decimal, percentile}`)."
    )
    lines.append("")
    lines.append(
        "The label-split walker is what unlocks biometric pairings: "
        "`fetuses[].measurements[].value` is emitted as one record per "
        "inherited label (BPD / AC / HC / Femur / ...), so each "
        "measurement label can pair with its corresponding HL7 identifier "
        "instead of being collapsed into a single multi-label record that "
        "matched nothing."
    )
    lines.append("")
    lines.append("### Paired rows by cluster")
    lines.append("")
    lines.append(f"_Total: {total_paired} paired cross-source rows._")
    lines.append("")
    lines.append("| cluster | paired |")
    lines.append("| --- | --- |")
    for cluster in [*cluster_order, "_unclustered"]:
        count = paired_by_cluster.get(cluster, 0)
        if count:
            lines.append(f"| {cluster} | {count} |")
    lines.append("")

    if biometry_pairs:
        lines.append("### Biometry pairings")
        lines.append("")
        lines.append(
            "Per-measurement Observer leaves paired with their HL7 "
            "namespace counterparts. Each row is one entry in the "
            "`biometry` cluster table below."
        )
        lines.append("")
        lines.append("| observer leaf | label | HL7 identifier |")
        lines.append("| --- | --- | --- |")
        for row in biometry_pairs:
            obs_leaf = escape_cell(
                row["observer_path"].rsplit(".", 1)[-1] or row["observer_path"]
            )
            label = escape_cell(row["observer_label_values"])
            vp = escape_cell(row["viewpoint_path"].removeprefix("OBX "))
            lines.append(f"| `{obs_leaf}` | {label} | `{vp}` |")
        lines.append("")

    lines.append("### Clusters with zero paired rows")
    lines.append("")
    lines.append(
        "Several clusters carry only Observer or only HL7 records: "
        "Observer-only `anatomy_general` / `fetal_procedures` cover "
        "JSON wrapper shapes (no HL7 namespace exists for them); "
        "HL7-only `anatomy_brain` / `anatomy_face_neck` / "
        "`anatomy_chest_gi` / `anatomy_spine` / `anatomy_urinary` "
        "cover HL7 namespaces whose Observer counterparts live under "
        "free-text `anomalies` fields rather than as structured leaves. "
        "Clusters with both sides populated but zero pairs (e.g. "
        "`placenta_cord`, `amniotic_fluid`, `dating`, `encounter`) "
        "tokenize differently on the two sides; tightening those would "
        "need a hand-curated alias map."
    )
    lines.append("")
    return lines


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
    lines.extend(
        render_clinician_overview(
            rows, cluster_order, SCRIPT_DIR / "concept_aliases.yaml"
        )
    )
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
    rows = load_rows()
    cluster_order = load_cluster_order()
    OUT_MD.write_text(render(rows, cluster_order), encoding="utf-8")
    logger.info("Wrote %s (%d rows ingested)", OUT_MD, len(rows))


if __name__ == "__main__":
    main()
