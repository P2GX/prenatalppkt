"""
Unit tests for scripts/parse_nichd_raw.py

These tests focus on verifying the parsing logic for the NIHCD
fetal growth calculator tables. They check whether headers/junk
are properly filtered and whether valid lines are correctly parsed
into structured rows.
"""

from prenatalppkt.scripts import parse_nichd_raw as nichd


def test_is_header_or_junk_detects_junk():
    """Ensure headers, junk markers, and page markers are detected correctly."""
    assert nichd.is_header_or_junk("Fetal Growth Calculator")
    assert nichd.is_header_or_junk("Age (weeks)")
    assert nichd.is_header_or_junk("3rd")  # standalone percentile
    assert nichd.is_header_or_junk("- 1 -")  # page marker
    assert not nichd.is_header_or_junk("20 White Abdominal Circ. 120 140 160 180")


def test_parse_line_valid_line():
    """Parse a valid line into GA, race, measure, and percentiles."""
    line = "20 White Abdominal Circ 120 140 160 180 200 220 240"
    row = nichd.parse_line(line)
    assert row is not None
    assert row[0] == "20"  # GA
    assert row[1] == "White"  # race
    assert "Abdominal" in row[2]  # measure normalized
    assert len(row) == 10  # GA + race + measure + 7 percentiles


def test_parse_line_junk_returns_none():
    """Ensure junk lines return None instead of being parsed."""
    line = "Percentile"
    assert nichd.parse_line(line) is None
