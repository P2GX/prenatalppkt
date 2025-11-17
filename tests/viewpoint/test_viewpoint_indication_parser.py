import pytest
from pathlib import Path
from prenatalppkt.parser.viewpoint.sections.viewpoint_indication_parse import (
    ViewpointIndicationParser,
)


def test_indication_simple():
    """Test parsing a simple single-line indication."""
    lines = [" ", "Known fetal cardiac abnormality", " "]
    parser = ViewpointIndicationParser(lines=lines)

    assert parser.indication == "Known fetal cardiac abnormality"
    assert len(parser.indication_items) == 1
    assert parser.indication_items[0] == "Known fetal cardiac abnormality"


def test_indication_multiline():
    """Test parsing an indication that spans multiple lines."""
    lines = [" ", "Known or suspected fetal anomaly.", "Interval fetal growth", " "]
    parser = ViewpointIndicationParser(lines=lines)

    # Should parse into two items
    assert len(parser.indication_items) == 2
    assert parser.indication_items[0] == "Known or suspected fetal anomaly."
    assert parser.indication_items[1] == "Interval fetal growth"

    # Full text should be combined
    expected = "Known or suspected fetal anomaly. Interval fetal growth"
    assert parser.indication == expected


def test_indication_with_periods():
    """Test parsing indication where lines already have periods."""
    lines = [" ", "Fetal Growth Restriction.", "Growth/Doppler", " "]
    parser = ViewpointIndicationParser(lines=lines)

    assert len(parser.indication_items) == 2
    assert parser.indication_items[0] == "Fetal Growth Restriction."
    assert parser.indication_items[1] == "Growth/Doppler"

    expected = "Fetal Growth Restriction. Growth/Doppler"
    assert parser.indication == expected


def test_indication_single_line_with_period():
    """Test parsing single line indication with multiple sentences."""
    lines = [" ", "Fetal Growth Restriction. Growth/Doppler", " "]
    parser = ViewpointIndicationParser(lines=lines)

    assert len(parser.indication_items) == 2
    assert "Fetal Growth Restriction." in parser.indication_items[0]
    assert "Growth/Doppler" in parser.indication_items[1]


def test_indication_complex():
    """Test parsing a more complex indication text."""
    lines = [" ", "Fetal CNS Malformation or Damage (Unspecified)", " "]
    parser = ViewpointIndicationParser(lines=lines)

    assert parser.indication == "Fetal CNS Malformation or Damage (Unspecified)"
    assert len(parser.indication_items) == 1


def test_indication_from_file():
    """Test parsing indication from the actual viewpoint test file."""
    # Load the test file
    data_path = (
        Path(__file__).resolve().parent.parent / "data" / "viewpoint_text_test.txt"
    )

    if not data_path.exists():
        pytest.skip(f"Test file not found: {data_path}")

    lines = data_path.read_text().splitlines()

    # Find the Indication section
    # Look for "Indication" followed by "========"
    indication_start = -1
    for i, line in enumerate(lines):
        if line.strip() == "Indication":
            if i + 1 < len(lines) and "===" in lines[i + 1]:
                indication_start = i + 2  # Start after the header and separator
                break

    assert indication_start > 0, "Could not find Indication section in file"

    # Extract lines until the next section or end of file
    indication_lines = []
    for i in range(indication_start, len(lines)):
        line = lines[i]
        # Stop at next section header (line before ===)
        if i + 1 < len(lines) and "===" in lines[i + 1]:
            break
        indication_lines.append(line)

    parser = ViewpointIndicationParser(lines=indication_lines)

    # Based on the test file content: "Fetal Growth Restriction. Growth/Doppler"
    assert len(parser.indication) > 0
    assert "Fetal Growth Restriction" in parser.indication
    assert "Growth/Doppler" in parser.indication
    assert len(parser.indication_items) >= 1


def test_indication_empty_raises_error():
    """Test that empty indication lines raise ValueError."""
    lines = [" ", "", " "]

    with pytest.raises(ValueError, match="No valid indication text found"):
        ViewpointIndicationParser(lines=lines)


def test_indication_repr():
    """Test the string representation of the parser."""
    lines = [" ", "Test indication", " "]
    parser = ViewpointIndicationParser(lines=lines)

    repr_str = repr(parser)
    assert "ViewpointIndicationParser" in repr_str
    assert "items=" in repr_str
    assert "Test indication" in repr_str


def test_indication_filters_section_headers():
    """Test that section headers are properly filtered out."""
    lines = [
        "Indication",
        "========",
        " ",
        "Fetal Sacrococcygeal Teratoma",
        " ",
        "History",
        "======",
    ]
    parser = ViewpointIndicationParser(lines=lines)

    assert parser.indication == "Fetal Sacrococcygeal Teratoma"
    assert len(parser.indication_items) == 1
    # Should NOT contain "Indication" or "History" in the parsed result
    assert "Indication" not in parser.indication
    assert "History" not in parser.indication


def test_indication_preserves_special_characters():
    """Test that special characters in indication are preserved."""
    lines = [" ", "Known anomaly (suspected). Growth/Doppler assessment", " "]
    parser = ViewpointIndicationParser(lines=lines)

    assert "Known anomaly (suspected)." in parser.indication
    assert "Growth/Doppler assessment" in parser.indication
    assert len(parser.indication_items) == 2


def test_indication_with_viewpoint_text_parser():
    """Test that the parser integrates correctly with ViewpointTextParse."""
    from prenatalppkt.parser.viewpoint.viewpoint_text_parser import ViewpointTextParse
    from prenatalppkt.parser.viewpoint.viewpoint_text_sections import SectionHeader

    data_path = (
        Path(__file__).resolve().parent.parent / "data" / "viewpoint_text_test.txt"
    )

    if not data_path.exists():
        pytest.skip(f"Test file not found: {data_path}")

    # Parse the file using ViewpointTextParse
    text_parser = ViewpointTextParse(input=data_path)

    # Get the Indication section
    indication_section = text_parser._section_d.get(SectionHeader.CLINICAL_INDICATIONS)

    if indication_section is None:
        pytest.skip("No Indication section found in test file")

    # Parse the indication section
    parser = ViewpointIndicationParser(lines=indication_section)

    # Verify we got valid indication text
    assert len(parser.indication) > 0
    assert len(parser.indication_items) >= 1
    assert (
        "Fetal Growth Restriction" in parser.indication
        or "Growth/Doppler" in parser.indication
    )
