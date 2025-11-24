"""
Tests for ViewPointTextExtractor.

Following TDD methodology for ViewPoint text file parsing.
"""

import pytest
from prenatalppkt.etl.extractors.viewpoint_text import ViewPointTextExtractor
from prenatalppkt.etl.models.biometry import BiometryCollection


class TestViewPointTextExtractor:
    """Test suite for ViewPoint text extraction."""

    @pytest.fixture
    def minimal_text(self):
        """Minimal ViewPoint text with single biometry."""
        return """
Indication
========

Fetal Growth

Fetal Biometry
============

HC                                                           233.7                  mm                         25w 1d                      36%                    Chervenak

General Evaluation
==============

Cardiac activity present.
"""

    @pytest.fixture
    def full_biometry_text(self):
        """Complete ViewPoint text with all biometries."""
        return """
Fetal Biometry
============

BPD                                                         63.2                    mm                         25w 4d                     36%                     Hadlock
OFD                                                         82.9                    mm                         25w 0d                     37%                     Nicolaides
HC                                                           233.7                  mm                         25w 1d                      36%                    Chervenak
AC                                                           221.0                  mm                         26w 4d                      67%                    Hadlock
Femur                                                      48.5                    mm                         26w 2d                      54%                    Hadlock
Humerus                                                  42.0                    mm                         25w 3d                      50%                    Hadlock

Head / Face / Neck Biometry:
Nuchal Fold                                           4.5                     mm                          25w 2d                      10%                     Standard
Cerebellum                                            30.0                    mm                         25w 3d                      40%                     Standard
"""

    @pytest.fixture
    def special_percentiles_text(self):
        """ViewPoint text with special percentile cases."""
        return """
Fetal Biometry
============

BPD                                                         76.6                    mm                         30w 5d                     <1%                    Hadlock
HC                                                           285.7                  mm                         30w 4d                      <1%                    Chervenak
AC                                                           289.6                  mm                         33w 0d                      2%                      Hadlock
Femur                                                      65.0                    mm                         33w 4d                      >99%                    Hadlock
"""

    def test_extract_returns_biometry_collection(self, minimal_text):
        """Test that extract returns BiometryCollection object."""
        extractor = ViewPointTextExtractor()
        result = extractor.extract(minimal_text)

        assert isinstance(result, BiometryCollection)

    def test_extract_single_hc_measurement(self, minimal_text):
        """Test extraction of single HC measurement."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(minimal_text)

        assert collection.count == 1

        hc = collection.get("HC")
        assert hc is not None
        assert hc.name == "HC"
        assert hc.value_mm == 233.7
        assert hc.percentile == 36.0
        assert hc.gestational_age == "G25w1d"
        assert hc.method == "Chervenak"

    def test_extract_all_eight_biometries(self, full_biometry_text):
        """Test extraction of all 8 target biometries."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(full_biometry_text)

        assert collection.count == 8

        expected_names = [
            "BPD",
            "OFD",
            "HC",
            "AC",
            "Femur",
            "Humerus",
            "Nuchal Fold",
            "Cerebellum",
        ]

        for name in expected_names:
            measurement = collection.get(name)
            assert measurement is not None, f"Missing {name}"
            assert measurement.value_mm > 0

    def test_percentile_parsing_normal_case(self, minimal_text):
        """Test parsing of normal percentile (e.g., '36%')."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(minimal_text)

        hc = collection.get("HC")
        assert hc.percentile == pytest.approx(36.0)

    def test_percentile_parsing_less_than_one(self, special_percentiles_text):
        """Test parsing of '<1%' percentile."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(special_percentiles_text)

        bpd = collection.get("BPD")
        hc = collection.get("HC")

        # '<1%' should be treated as 0.5
        assert bpd.percentile == pytest.approx(0.5)
        assert hc.percentile == pytest.approx(0.5)

    def test_percentile_parsing_greater_than_99(self, special_percentiles_text):
        """Test parsing of '>99%' percentile."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(special_percentiles_text)

        femur = collection.get("Femur")

        # '>99%' should be treated as 99.5
        assert femur.percentile == pytest.approx(99.5)

    def test_gestational_age_formatting(self, full_biometry_text):
        """Test gestational age formatting."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(full_biometry_text)

        bpd = collection.get("BPD")
        assert bpd.gestational_age == "G25w4d"

        ac = collection.get("AC")
        assert ac.gestational_age == "G26w4d"

    def test_method_extraction(self, full_biometry_text):
        """Test that measurement method is extracted."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(full_biometry_text)

        bpd = collection.get("BPD")
        assert bpd.method == "Hadlock"

        hc = collection.get("HC")
        assert hc.method == "Chervenak"

        ofd = collection.get("OFD")
        assert ofd.method == "Nicolaides"

    def test_unit_conversion_mm_unchanged(self, full_biometry_text):
        """Test that mm values stay in mm."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(full_biometry_text)

        bpd = collection.get("BPD")
        # Text shows 63.2 mm, should stay as 63.2 mm
        assert bpd.value_mm == pytest.approx(63.2)

    def test_no_biometry_section_returns_empty(self):
        """Test that text without biometry section returns empty collection."""
        text = """
Indication
========

Some indication text

General Evaluation
==============

No biometry section here.
"""

        extractor = ViewPointTextExtractor()
        collection = extractor.extract(text)

        assert collection.count == 0

    def test_fetus_number_is_none(self, minimal_text):
        """Test that ViewPoint text doesn't set fetus number."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(minimal_text)

        # ViewPoint text format doesn't include fetus number
        assert collection.fetus_number is None

        hc = collection.get("HC")
        assert hc.fetus_number is None

    def test_biometry_values_are_correct(self, full_biometry_text):
        """Test that all biometry values match expected values."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(full_biometry_text)

        expected_values = {
            "BPD": 63.2,
            "OFD": 82.9,
            "HC": 233.7,
            "AC": 221.0,
            "Femur": 48.5,
            "Humerus": 42.0,
            "Nuchal Fold": 4.5,
            "Cerebellum": 30.0,
        }

        for name, expected_value in expected_values.items():
            measurement = collection.get(name)
            assert measurement is not None, f"Missing {name}"
            assert measurement.value_mm == pytest.approx(expected_value), (
                f"{name} value mismatch"
            )

    def test_percentiles_are_correct(self, full_biometry_text):
        """Test that all percentiles match expected values."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract(full_biometry_text)

        expected_percentiles = {
            "BPD": 36.0,
            "OFD": 37.0,
            "HC": 36.0,
            "AC": 67.0,
            "Femur": 54.0,
            "Humerus": 50.0,
            "Nuchal Fold": 10.0,
            "Cerebellum": 40.0,
        }

        for name, expected_pct in expected_percentiles.items():
            measurement = collection.get(name)
            assert measurement is not None, f"Missing {name}"
            assert measurement.percentile == pytest.approx(expected_pct), (
                f"{name} percentile mismatch"
            )

    def test_malformed_line_skipped_gracefully(self):
        """Test that malformed lines don't crash the parser."""
        text = """
Fetal Biometry
============

HC                                                           233.7                  mm                         25w 1d                      36%                    Chervenak
This is a malformed line with not enough fields
BPD                                                         63.2                    mm                         25w 4d                     36%                     Hadlock
"""

        extractor = ViewPointTextExtractor()
        collection = extractor.extract(text)

        # Should extract HC and BPD, skip malformed line
        assert collection.count == 2
        assert collection.get("HC") is not None
        assert collection.get("BPD") is not None

    def test_empty_string_returns_empty_collection(self):
        """Test that empty string returns empty collection."""
        extractor = ViewPointTextExtractor()
        collection = extractor.extract("")

        assert collection.count == 0

    def test_invalid_input_type_raises_error(self):
        """Test that non-string input raises ValueError."""
        extractor = ViewPointTextExtractor()

        with pytest.raises(ValueError, match="Expected string"):
            extractor.extract({"not": "a string"})
