"""HL7 OBX-line parsing + type / value-class inference + file walker."""

from __future__ import annotations

from pathlib import Path

from .models import ViewpointField
from .observer import PERCENTILE_RE, WEEKS_DAYS_RE, add_sample, value_class


def parse_obx_line(line: str) -> tuple[str, str, str, str, str] | None:
    """Pipe-split one OBX line into (type, identifier, short, long, value) or None."""
    if not line.startswith("OBX|"):
        return None
    parts = line.rstrip("\r\n").split("|")
    if len(parts) < 6:
        return None
    obx_type = parts[2]
    id_parts = parts[3].split("^")
    identifier = id_parts[0]
    short_label = id_parts[1] if len(id_parts) > 1 else ""
    long_label = id_parts[2] if len(id_parts) > 2 else ""
    return obx_type, identifier, short_label, long_label, parts[5]


def display_hl7_value(raw_value: str) -> str:
    """Render `primary (secondary)` when the second caret-segment differs."""
    if not raw_value:
        return ""
    parts = raw_value.split("^")
    if len(parts) >= 2 and parts[1] and parts[1] != parts[0]:
        return f"{parts[0]} ({parts[1]})"
    return parts[0]


def hl7_observed_type(raw_value: str, obx_type: str) -> str:
    """JSON-shape-equivalent token for an HL7 OBX-5 value."""
    primary = raw_value.split("^", 1)[0] if raw_value else ""
    if primary == "":
        return "null"
    if obx_type == "NM":
        return "float" if "." in primary else "int"
    return "str"


def hl7_value_class(raw_value: str, identifier: str, obx_type: str) -> str:
    """Semantic class for an HL7 OBX value with identifier + OBX-2 hints."""
    parts = [part for part in raw_value.split("^") if part]
    search = " ".join(parts)
    if (
        any(PERCENTILE_RE.match(part) for part in parts)
        or "percentile" in identifier.lower()
    ):
        return "percentile"
    if any(WEEKS_DAYS_RE.match(part) for part in parts):
        return "weeks_days"
    if obx_type == "DT":
        return "date"
    if obx_type == "TM":
        return "time"
    if obx_type == "TS":
        return "timestamp"
    if obx_type == "NM":
        return "decimal" if "." in search else "integer"
    return value_class(search, identifier)


def walk_hl7_file(path: Path, fields: dict[str, ViewpointField]) -> int:
    """Parse one HL7 file; return the count of OBX rows seen."""
    count = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parsed = parse_obx_line(line)
            if parsed is None:
                continue
            obx_type, identifier, short_label, long_label, raw_value = parsed
            record = fields.setdefault(
                identifier, ViewpointField(identifier=identifier)
            )
            record.short_label = record.short_label or short_label
            record.long_label = record.long_label or long_label
            record.obx_types.add(obx_type)
            record.types.add(hl7_observed_type(raw_value, obx_type))
            record.value_classes.add(hl7_value_class(raw_value, identifier, obx_type))
            record.files.add(path.name)
            add_sample(record.samples, display_hl7_value(raw_value), record)
            count += 1
    return count
