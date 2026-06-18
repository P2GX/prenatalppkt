"""Tests for `extract.observer`: json_type, value_class, walk_observer."""

from __future__ import annotations

import pytest

from prenatalppkt.scripts.data_dict.extract.models import ObserverField
from prenatalppkt.scripts.data_dict.extract.observer import (
    json_type,
    value_class,
    walk_observer,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "null"),
        (True, "bool"),
        (False, "bool"),
        (1, "int"),
        (0, "int"),
        (3.14, "float"),
        ("hello", "str"),
        ("45%", "str"),
        ("20w 3d", "str"),
    ],
)
def test_json_type_canonical_shapes(value, expected):
    """All canonical JSON value shapes classify into the right raw token."""
    assert json_type(value) == expected


@pytest.mark.parametrize(
    ("value", "path", "expected"),
    [
        (None, "", "empty"),
        ("", "", "empty"),
        (True, "", "boolean"),
        (12, "", "integer"),
        (12.5, "", "decimal"),
        ("56%", "", "percentile"),
        ("<5%", "", "percentile"),
        (">95%", "", "percentile"),
        ("24w 0d", "", "weeks_days"),
        ("20250923", "Exam.ExamDate", "date"),
        ("2025-09-23", "", "date"),
        ("normal", "", "coded_text"),
        ("123456", "exam.exm_time", "time"),
    ],
)
def test_value_class_covers_common_shapes(value, path, expected):
    """Semantic classifier picks up percentiles, weeks+days, dates, integers, etc."""
    assert value_class(value, path) == expected


def test_value_class_long_string_is_free_text():
    """Strings longer than the coded-text cutoff fall into free_text."""
    long_text = "x" * 81
    assert value_class(long_text) == "free_text"


def test_walk_observer_records_scalar_leaves_and_labels():
    """The walker records each scalar leaf keyed by (path, inherited-label)."""
    fields: dict[tuple[str, str], ObserverField] = {}
    walk_observer(
        {"fetuses": [{"measurements": [{"label": "BPD", "value": 6.1}]}]},
        "",
        "case.json",
        fields,
    )
    assert ("fetuses[].measurements[].value", "BPD") in fields
    record = fields[("fetuses[].measurements[].value", "BPD")]
    assert record.label == "BPD"
    assert "float" in record.types
    assert "decimal" in record.value_classes
    assert record.files == {"case.json"}


def test_walk_observer_splits_measurements_by_label():
    """Two measurements with different labels become two distinct records."""
    fields: dict[tuple[str, str], ObserverField] = {}
    walk_observer(
        {
            "fetuses": [
                {
                    "measurements": [
                        {"label": "BPD", "value": 45.2},
                        {"label": "AC", "value": 163.0},
                    ]
                }
            ]
        },
        "",
        "case.json",
        fields,
    )
    assert ("fetuses[].measurements[].value", "BPD") in fields
    assert ("fetuses[].measurements[].value", "AC") in fields
    assert fields[("fetuses[].measurements[].value", "BPD")].label == "BPD"
    assert fields[("fetuses[].measurements[].value", "AC")].label == "AC"


def test_walk_observer_dedupes_samples_across_files():
    """A repeated value should not appear twice in the sample list."""
    fields: dict[tuple[str, str], ObserverField] = {}
    walk_observer({"k": "v"}, "", "a.json", fields)
    walk_observer({"k": "v"}, "", "b.json", fields)
    record = fields[("k", "")]
    assert record.samples == ["v"]
    assert record.files == {"a.json", "b.json"}


def test_walk_observer_dict_dives_into_children():
    """Dict containers do not become leaf records; their scalar children do."""
    fields: dict[tuple[str, str], ObserverField] = {}
    walk_observer(
        {"exam": {"fetus_count": 1, "site_name": "CUIMC"}}, "", "file1.json", fields
    )
    assert ("exam.fetus_count", "") in fields
    assert ("exam.site_name", "") in fields
    assert ("exam", "") not in fields
    assert ("fetuses", "") not in fields
