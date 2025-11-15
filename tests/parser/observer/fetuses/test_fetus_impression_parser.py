"""Unit tests for FetusImpressionParser."""

from prenatalppkt.parser.observer.fetuses import FetusImpressionParser
from prenatalppkt.dto.observer.fetuses.fetus_impression_data import FetusImpressionData


def test_parse_impression_as_string():
    """Test parsing impression when it's a simple string."""
    parser = FetusImpressionParser()
    input_json = {"impression": "Normal anatomy scan"}
    result = parser.parse(input_json)

    assert isinstance(result, FetusImpressionData)
    assert result.impression_text == "Normal anatomy scan"
    assert result.is_present


def test_parse_impression_as_list():
    """Test parsing impression when it's a list of strings."""
    parser = FetusImpressionParser()
    input_json = {"impression": ["Finding 1", "Finding 2", "Finding 3"]}
    result = parser.parse(input_json)

    assert isinstance(result, FetusImpressionData)
    assert result.impressions == ["Finding 1", "Finding 2", "Finding 3"]
    assert len(result.impressions) == 3
    assert result.is_present


def test_parse_impression_with_fetus_number():
    """Test that fetus_number is extracted when available."""
    parser = FetusImpressionParser()
    input_json = {"fetus": {"fetus_number": 1}, "impression": "Normal findings"}
    result = parser.parse(input_json)

    assert isinstance(result, FetusImpressionData)
    assert result.fetus_number == 1
    assert result.impression_text == "Normal findings"


def test_parse_missing_impression():
    """Test that None is returned when impression key is missing."""
    parser = FetusImpressionParser()
    result = parser.parse({})
    assert result is None


def test_parse_empty_string_impression():
    """Test that None is returned for empty string impression."""
    parser = FetusImpressionParser()
    result = parser.parse({"impression": ""})
    assert result is None


def test_parse_empty_list_impression():
    """Test that None is returned for empty list impression."""
    parser = FetusImpressionParser()
    result = parser.parse({"impression": []})
    assert result is None


def test_parse_malformed_input():
    """Test that ValueError is raised for non-dict input."""
    parser = FetusImpressionParser()
    try:
        parser.parse("not a dict")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "malformed argument" in str(e)
