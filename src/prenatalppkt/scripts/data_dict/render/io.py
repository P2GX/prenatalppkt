"""CSV loading, cluster order, cluster grouping, and Markdown cell escaping."""

from __future__ import annotations

import csv
from collections import OrderedDict
from pathlib import Path

import yaml


def escape_cell(value: str) -> str:
    """Escape characters that would otherwise break a Markdown table cell."""
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def load_cluster_order(path: Path) -> list[str]:
    """YAML-declared cluster names in the order the README should render them."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [entry["cluster"] for entry in data]


def load_rows(path: Path) -> list[dict[str, str]]:
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
