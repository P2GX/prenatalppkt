"""Tests for `extract_all.py`: type detection, OBX parsing, cluster matching."""

from __future__ import annotations

from collections import defaultdict

import pytest

from prenatalppkt.scripts.data_dict.extract_all import (
    UNCLUSTERED,
    classify_observer,
    classify_viewpoint,
    coverage,
    detect_hl7_string_type,
    detect_json_type,
    format_sample,
    format_types,
    hl7_value_primary,
    parse_obx_line,
    primary_identifier,
    viewpoint_type_signature,
    walk_observer,
)


# -----------------------
# Type detection
# -----------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "null"),
        (True, "bool"),
        (False, "bool"),
        (1, "int"),
        (0, "int"),
        (3.14, "float"),
        ([], "list"),
        ([1, 2], "list"),
        ({}, "dict"),
        ({"a": 1}, "dict"),
        ("hello", "str"),
        ("45%", "percentile_str"),
        ("-3.5%", "percentile_str"),
        ("<5%", "percentile_str"),
        (">95%", "percentile_str"),
        ("20w 3d", "weeks_days_str"),
        ("0w 0d", "weeks_days_str"),
    ],
)
def test_detect_json_type(value, expected):
    """All canonical JSON value shapes classify into the right token."""
    assert detect_json_type(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", "null"),
        ("Normal", "str"),
        ("45%", "percentile_str"),
        ("20w 3d", "weeks_days_str"),
    ],
)
def test_detect_hl7_string_type(value, expected):
    """Empty HL7 strings classify as null, non-empty fall through to JSON detector."""
    assert detect_hl7_string_type(value) == expected


# -----------------------
# Cluster matching
# -----------------------


@pytest.fixture
def clusters():
    """Two-cluster fixture exercising first-match-wins and the unclustered fallback."""
    return [
        {
            "cluster": "biometry",
            "observer_prefixes": ["fetuses[].measurements"],
            "viewpoint_prefixes": ["SkullFetus"],
        },
        {
            "cluster": "anatomy",
            "observer_prefixes": ["fetuses[].anatomy[]"],
            "viewpoint_prefixes": ["BrainFetus", "FaceFetus"],
        },
    ]


def test_classify_observer_first_match_wins(clusters):
    """The first cluster whose prefix list contains a hit wins."""
    assert classify_observer("fetuses[].measurements[].value", clusters) == "biometry"
    assert classify_observer("fetuses[].anatomy[].brain.choroid", clusters) == "anatomy"


def test_classify_observer_unmatched_path_is_unclustered(clusters):
    """A path matching no prefix lands in the _unclustered bucket."""
    assert classify_observer("hist_phys_vitals.weight", clusters) == UNCLUSTERED


def test_classify_viewpoint_matches_prefix(clusters):
    """HL7 identifiers route through the same first-match-wins logic."""
    assert classify_viewpoint("SkullFetus.BPD", clusters) == "biometry"
    assert classify_viewpoint("FaceFetus.Profile", clusters) == "anatomy"
    assert classify_viewpoint("WarningMessage", clusters) == UNCLUSTERED


# -----------------------
# HL7 parsing
# -----------------------


def test_parse_obx_line_well_formed():
    """A canonical OBX line decomposes into (type, identifier, value)."""
    line = "OBX|1|NM|SkullFetus.BPD^BPD^Biparietal diameter|Fetus1|45.2^45.2||||F\r\n"
    result = parse_obx_line(line)
    assert result == ("NM", "SkullFetus.BPD^BPD^Biparietal diameter", "45.2^45.2")


def test_parse_obx_line_non_obx_returns_none():
    """Non-OBX segments are skipped."""
    assert parse_obx_line("MSH|^~\\&|GE|...\r\n") is None
    assert parse_obx_line("PID|1||12345\r\n") is None


def test_parse_obx_line_too_short_returns_none():
    """A truncated OBX line missing required fields is rejected."""
    assert parse_obx_line("OBX|1|NM|FOO\r\n") is None


def test_primary_identifier_strips_caret_tail():
    """Only the first `^` segment of OBX-3 is the canonical identifier."""
    assert primary_identifier("SkullFetus.BPD^BPD^Biparietal") == "SkullFetus.BPD"
    assert primary_identifier("PlainIdentifier") == "PlainIdentifier"


def test_hl7_value_primary_unwraps_doubled_numeric():
    """HL7 NM values are stored as `value^value`; sample on the leading half."""
    assert hl7_value_primary("45.2^45.2") == "45.2"
    assert hl7_value_primary("") == ""
    assert hl7_value_primary("just text") == "just text"


# -----------------------
# Observer walker
# -----------------------


def test_walk_observer_records_types_and_samples():
    """The walker fans out by key, dedupes samples, and remembers value types."""
    acc: dict[str, dict] = defaultdict(dict)
    doc = {
        "exam": {"fetus_count": 1, "site_name": "CUIMC"},
        "fetuses": [{"measurements": [{"label": "BPD", "value": 45.2}]}],
    }
    walk_observer(doc, "", "file1.json", acc)
    assert "exam.fetus_count" in acc
    assert "int" in acc["exam.fetus_count"]["observed_types"]
    assert 1 in acc["exam.fetus_count"]["value_set_sample"]
    assert "str" in acc["exam.site_name"]["observed_types"]
    assert "float" in acc["fetuses[].measurements[].value"]["observed_types"]
    assert acc["fetuses[].measurements[].label"]["files_present"] == {"file1.json"}


def test_walk_observer_dedupes_samples_across_files():
    """A repeated value should not appear twice in the sample list."""
    acc: dict[str, dict] = defaultdict(dict)
    walk_observer({"k": "v"}, "", "a.json", acc)
    walk_observer({"k": "v"}, "", "b.json", acc)
    assert acc["k"]["value_set_sample"] == ["v"]
    assert acc["k"]["files_present"] == {"a.json", "b.json"}


# -----------------------
# Row formatting
# -----------------------


def test_format_types_joins_sorted():
    """Observed-type tokens render pipe-joined in sorted order."""
    record = {"observed_types": {"int", "float", "null"}}
    assert format_types(record) == "float|int|null"


def test_format_sample_appends_overflow_marker():
    """A truncated value-set shows `...` so downstream readers know about it."""
    record = {"value_set_sample": ["a", "b"], "value_overflow": True}
    assert format_sample(record) == "a|b|..."


def test_format_sample_empty_returns_empty_string():
    """No samples means an empty CSV cell, not `None` or `[]`."""
    assert format_sample({}) == ""


def test_viewpoint_type_signature_combines_observed_and_obx_declared():
    """Viewpoint cells embed the declared OBX-2 type in parens."""
    record = {"observed_types": {"float", "null"}, "hl7_obx_types": {"NM"}}
    assert viewpoint_type_signature(record) == "float|null (NM)"


def test_viewpoint_type_signature_no_obx_falls_back_to_observed():
    """If no OBX-2 types were ever seen, only observed types render."""
    record = {"observed_types": {"str"}}
    assert viewpoint_type_signature(record) == "str"


def test_coverage_formats_present_over_total():
    """File coverage renders as `present/total`."""
    record = {"files_present": {"a.json", "b.json", "c.json"}}
    assert coverage(record, 5) == "3/5"
