"""Plain-language clinician-facing cross-source field map."""

from __future__ import annotations

from pathlib import Path

import yaml

from .constants import CLUSTER_TEMPLATE_GUIDANCE, VALUE_CLASS_LABEL
from .io import escape_cell


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
    lines.append("Plain-language map of the data this pipeline ingests.")
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
    lines.append("### Concepts both systems capture (or only one side does)")
    lines.append("")
    lines.append(
        f"The {len(raw_aliases)} hand-curated concepts in "
        "`concept_aliases.yaml`, sorted by clinical area. "
        "`(Observer-only)` / `(ViewPoint-only)` mark where only one "
        "source has the field."
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

    lines.append("### Designing an XLSX template from this dictionary")
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
        "- **The XLSX is upstream of the ETL.** Once it exists, a "
        "PhenoXtract-style YAML config wraps it back into Phenopackets "
        "via the same data dictionary you're reading now."
    )
    lines.append("")
    return lines
