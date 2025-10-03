"""
Unit tests for scripts/parse_intergrowth_txt_all.py

These tests validate the rule-based parsing of Intergrowth-21
tables in plain text form. They check centile and z-score parsing,
header matching, TSV writing, and summary bookkeeping.
"""

import pandas as pd
from pathlib import Path
from prenatalppkt.scripts import parse_intergrowth_txt_all as intergrowth


# -------------------
# Helper sample lines
# -------------------


def sample_ct_lines():
    """Provide two synthetic centile rows with correct structure."""
    return ["14 100 110 120 130 140 150 160", "15 101 111 121 131 141 151 161"]


def sample_zs_lines():
    """Provide two synthetic z-score rows with correct structure."""
    return ["14 -3 -2 -1 0 1 2 3", "15 -2.9 -1.9 -0.9 0.1 1.1 2.1 3.1"]


# ----------------------
# Individual unit tests
# ----------------------


def test_parse_table_ct():
    """Verify centile table parsing produces expected columns and values."""
    summary = {}
    df = intergrowth.parse_table(
        sample_ct_lines(),
        intergrowth.CT_HEADERS,
        measure="Head Circumference",
        source="test_ct.txt",
        summary=summary,
    )
    assert not df.empty
    assert "Head Circumference" in df["Measure"].unique()
    assert all(col in df.columns for col in intergrowth.CT_HEADERS)
    assert df["Gestational Age (weeks)"].iloc[0] == 14


def test_parse_table_zs():
    """Verify z-score table parsing produces expected columns and numeric coercion."""
    summary = {}
    df = intergrowth.parse_table(
        sample_zs_lines(),
        intergrowth.ZS_HEADERS,
        measure="Biparietal Diameter",
        source="test_zs.txt",
        summary=summary,
    )
    assert not df.empty
    assert "Biparietal Diameter" in df["Measure"].unique()
    assert all(col in df.columns for col in intergrowth.ZS_HEADERS)
    # Confirm numeric coercion worked
    assert df["0 SD"].iloc[1] == 0.1


def test_parse_txt_file_roundtrip(tmp_path: Path):
    """Write a fake text file and ensure parse_txt_file reads and parses it correctly."""
    file_path = tmp_path / "grow_fetal-ct_ac_table.txt"
    file_path.write_text("\n".join(sample_ct_lines()))

    summary = {}
    df = intergrowth.parse_txt_file(file_path, "Abdominal Circumference", "ct", summary)
    assert not df.empty
    assert "Abdominal Circumference" in df["Measure"].unique()
    assert file_path.name in summary


def test_write_tsv_creates_file(tmp_path: Path):
    """Ensure DataFrame is written to disk as TSV with correct headers."""
    df = pd.DataFrame(
        {
            "Gestational Age (weeks)": [14, 15],
            "Measure": ["HC", "HC"],
            "50th Percentile": [130, 131],
        }
    )
    out_path = tmp_path / "out.tsv"
    intergrowth.write_tsv(df, out_path)
    assert out_path.exists()
    content = out_path.read_text()
    assert "50th Percentile" in content
