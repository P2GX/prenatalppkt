"""Concept-alias YAML loading (Observer + Viewpoint -> concept_key lookup tables)."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_concept_aliases(
    path: Path,
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
