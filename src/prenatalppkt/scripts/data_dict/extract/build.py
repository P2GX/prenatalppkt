"""Row formatting + cross-cluster row builder for comparison.csv."""

from __future__ import annotations

from collections import defaultdict

from .clusters import UNCLUSTERED, classify_observer, classify_viewpoint
from .models import Cluster, ObserverField, ViewpointField
from .pairing import pair_fields


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
