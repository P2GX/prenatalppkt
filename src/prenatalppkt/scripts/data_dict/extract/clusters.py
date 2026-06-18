"""Cluster YAML loading + per-record cluster classification."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import Cluster

UNCLUSTERED = "_unclustered"


def load_clusters(path: Path) -> list[Cluster]:
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
