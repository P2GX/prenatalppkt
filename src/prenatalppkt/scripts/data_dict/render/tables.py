"""Markdown table rendering for one cluster's paired rows."""

from __future__ import annotations

from .constants import TABLE_COLUMNS
from .io import escape_cell


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
