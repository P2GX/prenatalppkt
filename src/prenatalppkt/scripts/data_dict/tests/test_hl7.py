"""Tests for `extract.hl7`: OBX parsing, display formatting, type/value-class inference."""

from __future__ import annotations

import pytest

from prenatalppkt.scripts.data_dict.extract.hl7 import (
    display_hl7_value,
    hl7_observed_type,
    hl7_value_class,
    parse_obx_line,
)


def test_parse_obx_keeps_identifier_short_long_and_value():
    """A canonical OBX-3 splits into (type, identifier, short_label, long_label, value)."""
    parsed = parse_obx_line(
        "OBX|1|NM|SkullFetus.BiparietalDiameter^BPD^Biparietal diameter"
        "|Fetus1|62.1^62.1|mm&millimeters||||||||20250923"
    )
    assert parsed == (
        "NM",
        "SkullFetus.BiparietalDiameter",
        "BPD",
        "Biparietal diameter",
        "62.1^62.1",
    )


def test_parse_obx_line_non_obx_returns_none():
    """Non-OBX segments are skipped."""
    assert parse_obx_line("MSH|^~\\&|GE|...\r\n") is None
    assert parse_obx_line("PID|1||12345\r\n") is None


def test_parse_obx_line_too_short_returns_none():
    """A truncated OBX line missing required fields is rejected."""
    assert parse_obx_line("OBX|1|NM|FOO\r\n") is None


def test_display_hl7_value_renders_secondary_when_distinct():
    """If the second caret-segment carries unit context, render `primary (secondary)`."""
    assert display_hl7_value("163^24w 0d") == "163 (24w 0d)"
    assert display_hl7_value("0^<1%") == "0 (<1%)"
    assert display_hl7_value("") == ""


def test_display_hl7_value_unwraps_doubled_numeric():
    """When primary == secondary (typical NM), the display collapses to the primary."""
    assert display_hl7_value("45.2^45.2") == "45.2"
    assert display_hl7_value("just text") == "just text"


@pytest.mark.parametrize(
    ("raw_value", "obx_type", "expected"),
    [
        ("", "ST", "null"),
        ("45.2^45.2", "NM", "float"),
        ("62^62", "NM", "int"),
        ("Normal", "ST", "str"),
    ],
)
def test_hl7_observed_type(raw_value, obx_type, expected):
    """OBX-5 value + OBX-2 declared type map to a JSON-shape token."""
    assert hl7_observed_type(raw_value, obx_type) == expected


def test_hl7_value_class_uses_display_percentile():
    """Percentile and weeks_days fire from the second caret-segment / identifier hints."""
    assert hl7_value_class("0^<1%", "Fetus.VP_Field_Percentile", "NM") == "percentile"
    assert (
        hl7_value_class("168^24w 0d", "ExamOBDating.GestationalAgeDaysAgreed", "NM")
        == "weeks_days"
    )


def test_hl7_value_class_numeric_split():
    """An NM value with a decimal point reads as decimal, otherwise integer."""
    assert hl7_value_class("45.2^45.2", "SkullFetus.BPD", "NM") == "decimal"
    assert hl7_value_class("45^45", "SkullFetus.BPD", "NM") == "integer"
