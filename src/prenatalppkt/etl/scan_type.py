"""Scan-type classifier for Observer JSON exports.

Historically each caller detected first-trimester scans via its own
local heuristic and skipped them; the extractor here just raised a
generic ValueError when biometry was missing. Lifting the classifier
into the library lets every caller (CLI, future TUI, Beacon endpoint)
reach the same verdict from the same code path.

The enum is deliberately minimal: only the distinctions the extractor
acts on today (FIRST_TRIMESTER vs T2_T3_BIOMETRY) plus UNKNOWN for
partial / malformed inputs. ANATOMY_SURVEY vs GROWTH_SCAN splits stay
deferred until a code path needs them.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from prenatalppkt.etl.constants import OBSERVER_NAME_MAP

# Canonical measurement names (BiometryMeasurement values). Raw Observer labels
# are normalized through OBSERVER_NAME_MAP before comparison, so wire-label
# variants like "FL" (femur) classify the same as "Femur".
T1_LABELS = frozenset({"CRL", "NT"})
T2T3_REQUIRED_LABELS = frozenset({"AC", "BPD", "HC", "Femur"})


def _canonical_labels(measurements: list[dict[str, Any]]) -> set[str]:
    """Collect standard measurement names from a fetus's measurement list.

    Each raw label/name is mapped through OBSERVER_NAME_MAP when known; unknown
    labels are kept as-is so they simply fail to match the standard sets.
    """
    canonical: set[str] = set()
    for m in measurements:
        raw = m.get("label") or m.get("name")
        if raw is None:
            continue
        member = OBSERVER_NAME_MAP.get(raw)
        canonical.add(member.value if member is not None else raw)
    return canonical


class ScanType(Enum):
    """Routing classifier for the ETL pipeline."""

    FIRST_TRIMESTER = "first_trimester"
    T2_T3_BIOMETRY = "t2_t3_biometry"
    UNKNOWN = "unknown"


class UnsupportedScanTypeError(ValueError):
    """Raised when the scan type is detectable but no ETL path exists for it.

    Subclasses ValueError so existing `except ValueError` callers keep working.
    """


def classify_fetus(fetus_data: dict[str, Any]) -> ScanType:
    """Classify a single fetus dict by its measurement labels.

    Rules:
      - Has CRL or NT and lacks the full T2/T3 set -> FIRST_TRIMESTER
      - Has all of {AC, BPD, HC, Femur}             -> T2_T3_BIOMETRY
      - Otherwise                                   -> UNKNOWN

    Twin exams carry fetuses with different scan types, so classification must
    run per fetus, not once for the whole exam.
    """
    measurements = fetus_data.get("measurements") or []
    labels = _canonical_labels(measurements)

    if T2T3_REQUIRED_LABELS.issubset(labels):
        return ScanType.T2_T3_BIOMETRY

    if labels & T1_LABELS:
        return ScanType.FIRST_TRIMESTER

    return ScanType.UNKNOWN


def detect_scan_type(observer_json: dict[str, Any]) -> ScanType:
    """Classify an Observer JSON dict by inspecting the first fetus's labels."""
    fetuses = observer_json.get("fetuses") or []
    if not fetuses:
        return ScanType.UNKNOWN
    return classify_fetus(fetuses[0])
