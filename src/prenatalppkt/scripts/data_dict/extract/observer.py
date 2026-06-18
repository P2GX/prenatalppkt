"""Observer JSON walker: label-split, type detection, semantic value classes."""

from __future__ import annotations

import re
from typing import Any

from .models import ObserverField

SAMPLE_LIMIT = 10

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{8}$")
TIME_RE = re.compile(r"^\d{6}$")
TIMESTAMP_RE = re.compile(r"^\d{14}$")
DECIMAL_RE = re.compile(r"^-?\d+\.\d+$")
INTEGER_RE = re.compile(r"^-?\d+$")
PERCENTILE_RE = re.compile(r"^(?:-?\d+(?:\.\d+)?%|[<>]\d+%)$")
WEEKS_DAYS_RE = re.compile(r"^\d+w \d+d$")


def json_type(value: Any) -> str:
    """Raw JSON shape token: null / bool / int / float / str."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    return "str"


def value_class(value: Any, path: str = "") -> str:  # noqa: C901
    """Semantic class with path-name hints (percentile, weeks_days, date, ...)."""
    if value is None or value == "":
        return "empty"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "decimal"
    text = str(value).strip()
    lower_path = path.lower()
    if PERCENTILE_RE.match(text) or "percentile" in lower_path:
        return "percentile"
    if WEEKS_DAYS_RE.match(text) or "gestationalage" in lower_path:
        return "weeks_days"
    if DATE_RE.match(text) or lower_path.endswith("date") or "date" in lower_path:
        return "date"
    if TIME_RE.match(text) or TIMESTAMP_RE.match(text) or "time" in lower_path:
        return "time"
    if DECIMAL_RE.match(text):
        return "decimal"
    if INTEGER_RE.match(text):
        return "integer"
    if len(text) > 80 or "\\.br\\" in text or "\n" in text:
        return "free_text"
    return "coded_text"


def _next_label(value: Any, current: str) -> str:
    """Pick up `label` field on a dict node; otherwise inherit `current`."""
    if isinstance(value, dict):
        lbl = value.get("label")
        if isinstance(lbl, (str, int, float)) and str(lbl):
            return str(lbl)
    return current


def add_sample(samples: list[str], value: str, record: Any) -> None:
    """Append `value` to `samples` (deduped, capped at SAMPLE_LIMIT, overflow flag)."""
    if value == "":
        return
    if value not in samples and len(samples) < SAMPLE_LIMIT:
        samples.append(value)
    elif value not in samples:
        record.overflow = True


def walk_observer(
    value: Any,
    path: str,
    file_name: str,
    fields: dict[tuple[str, str], ObserverField],
    label_ctx: str = "",
) -> None:
    """Recursive descent; one record per (path, inherited-label) at each leaf."""
    next_ctx = _next_label(value, label_ctx)
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{path}.{key}" if path else key
            walk_observer(value[key], child, file_name, fields, next_ctx)
        return
    if isinstance(value, list):
        child = f"{path}[]" if path else "[]"
        for item in value:
            walk_observer(item, child, file_name, fields, next_ctx)
        return

    if not path:
        return
    key = (path, label_ctx)
    record = fields.setdefault(key, ObserverField(path=path, label=label_ctx))
    record.types.add(json_type(value))
    record.value_classes.add(value_class(value, path))
    record.files.add(file_name)
    if value is not None:
        add_sample(record.samples, str(value), record)
