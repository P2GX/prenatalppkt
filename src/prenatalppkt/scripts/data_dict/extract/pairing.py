"""Greedy first-fit pairing keyed on token overlap + compatible value classes."""

from __future__ import annotations

import re

from .models import ObserverField, ViewpointField


def normalize_token(text: str) -> str:
    """Collapse a name into a lower-snake-case token for matching."""
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", text)
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).lower()
    return re.sub(r"_+", "_", text).strip("_")


def observer_match_tokens(record: ObserverField) -> set[str]:
    """Tokens from path leaf + inherited label (label always included if set)."""
    tokens = {normalize_token(record.path.rsplit(".", 1)[-1])}
    if record.label:
        tokens.add(normalize_token(record.label))
    return {t for t in tokens if t}


def viewpoint_match_tokens(record: ViewpointField) -> set[str]:
    """Tokens from identifier leaf + short_label + long_label."""
    pieces = [
        record.identifier.rsplit(".", 1)[-1],
        record.short_label,
        record.long_label,
    ]
    return {t for t in (normalize_token(p) for p in pieces) if t}


def compatible_classes(left: set[str], right: set[str]) -> bool:
    """Either a direct class overlap, or both sides have any numeric class."""
    if left & right:
        return True
    numeric = {"integer", "decimal", "percentile"}
    return bool(left & numeric and right & numeric)


def pair_fields(
    observers: list[ObserverField], viewpoints: list[ViewpointField]
) -> list[tuple[ObserverField | None, ViewpointField | None]]:
    """Greedy first-fit pairing keyed on token overlap + compatible value classes."""
    remaining = list(viewpoints)
    pairs: list[tuple[ObserverField | None, ViewpointField | None]] = []
    for observer in observers:
        observer_tokens = observer_match_tokens(observer)
        candidates: list[tuple[int, str, ViewpointField]] = []
        for viewpoint in remaining:
            shared = observer_tokens & viewpoint_match_tokens(viewpoint)
            if not shared:
                continue
            if not compatible_classes(observer.value_classes, viewpoint.value_classes):
                continue
            score = len(shared)
            if observer.label and normalize_token(observer.label) in shared:
                score += 3
            if normalize_token(observer.path.rsplit(".", 1)[-1]) in shared:
                score += 1
            candidates.append((score, viewpoint.identifier, viewpoint))
        if candidates:
            candidates.sort(key=lambda item: (-item[0], item[1]))
            match = candidates[0][2]
            remaining.remove(match)
            pairs.append((observer, match))
        else:
            pairs.append((observer, None))
    pairs.extend((None, viewpoint) for viewpoint in remaining)
    return pairs
