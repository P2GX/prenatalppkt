"""Pairing methodology section + per-cluster paired counts + biometry table."""

from __future__ import annotations

from .io import escape_cell


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
