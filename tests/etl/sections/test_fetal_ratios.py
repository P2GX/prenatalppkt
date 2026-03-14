"""Tests for fetal ratios section parser."""

import json
import pytest

from prenatalppkt.etl.sections.fetal_ratios import parse_fetal_ratios


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


class TestFetalRatiosObserver:
    def test_basic_ratios(self):
        """Test parsing of basic ratio data."""
        data = {
            "fetuses": [
                {
                    "ratios": [
                        {
                            "label": "HC/AC",
                            "value": 1.105,
                            "range": "1.04 - 1.22",
                            "fetus_number": 1,
                        },
                        {
                            "label": "FL/AC",
                            "value": 22.149,
                            "range": "20 - 24",
                            "fetus_number": 1,
                        },
                        {
                            "label": "FL/BPD",
                            "value": 75,
                            "range": "71 - 87",
                            "fetus_number": 1,
                        },
                    ]
                }
            ]
        }

        result = parse_fetal_ratios(data, "observer_json")

        assert len(result["ratios"]) == 3
        assert result["all_within_range"] is True
        assert result["proportionality_assessment"] == "Normal"
        assert result["source_format"] == "observer_json"

        # Check specific ratio
        hc_ac = next(r for r in result["ratios"] if r["name"] == "HC/AC")
        assert hc_ac["value"] == 1.105
        assert hc_ac["expected_range"] == (1.04, 1.22)
        assert hc_ac["within_range"] is True

    def test_ratio_out_of_range(self):
        """Test detection of out-of-range ratio."""
        data = {
            "fetuses": [
                {
                    "ratios": [
                        {
                            "label": "HC/AC",
                            "value": 1.35,  # Above normal range
                            "range": "1.04 - 1.22",
                            "fetus_number": 1,
                        }
                    ]
                }
            ]
        }

        result = parse_fetal_ratios(data, "observer_json")

        assert result["all_within_range"] is False
        assert result["proportionality_assessment"] == "Asymmetric"
        assert result["ratios"][0]["within_range"] is False

    def test_asymmetric_growth_detection(self):
        """Test asymmetric growth pattern detection via HC/AC."""
        data = {
            "fetuses": [
                {
                    "ratios": [
                        {
                            "label": "HC/AC",
                            "value": 0.95,  # Below normal - head-sparing
                            "range": "1.04 - 1.22",
                        },
                        {
                            "label": "FL/BPD",
                            "value": 80,  # Within range
                            "range": "71 - 87",
                        },
                    ]
                }
            ]
        }

        result = parse_fetal_ratios(data, "observer_json")

        assert result["proportionality_assessment"] == "Asymmetric"

    def test_json_string_input(self):
        """Test that JSON string input is handled correctly."""
        data = json.dumps(
            {
                "fetuses": [
                    {
                        "ratios": [
                            {"label": "HC/AC", "value": 1.1, "range": "1.04 - 1.22"}
                        ]
                    }
                ]
            }
        )

        result = parse_fetal_ratios(data, "observer_json")

        assert len(result["ratios"]) == 1

    def test_empty_fetuses(self):
        """Test handling of empty fetuses array."""
        data = {"fetuses": []}

        result = parse_fetal_ratios(data, "observer_json")

        assert result["ratios"] == []
        assert result["all_within_range"] is None

    def test_missing_ratios_key(self):
        """Test handling of fetus without ratios key."""
        data = {"fetuses": [{"fetus": {}}]}

        result = parse_fetal_ratios(data, "observer_json")

        assert result["ratios"] == []

    def test_ratio_without_range(self):
        """Test handling of ratio without expected range."""
        data = {
            "fetuses": [
                {
                    "ratios": [
                        {
                            "label": "HC/AC",
                            "value": 1.1,
                            "range": "",  # Empty range
                        }
                    ]
                }
            ]
        }

        result = parse_fetal_ratios(data, "observer_json")

        assert result["ratios"][0]["expected_range"] is None
        assert result["ratios"][0]["within_range"] is None

    def test_boundary_values(self):
        """Test boundary values at exactly min and max of range."""
        data = {
            "fetuses": [
                {
                    "ratios": [
                        {
                            "label": "HC/AC",
                            "value": 1.04,
                            "range": "1.04 - 1.22",
                        },  # At min
                        {"label": "FL/AC", "value": 24, "range": "20 - 24"},  # At max
                    ]
                }
            ]
        }

        result = parse_fetal_ratios(data, "observer_json")

        assert all(r["within_range"] for r in result["ratios"])


# ---------------------------------------------------------------------
# ViewPoint Text (Skeleton)
# ---------------------------------------------------------------------


class TestFetalRatiosViewPointText:
    def test_skeleton_parses_ratio_pattern(self):
        """Test that skeleton can parse basic ratio patterns."""
        text = """Fetal Biometry
============
FL / HC    0.23
"""

        result = parse_fetal_ratios(text, "viewpoint_text")

        assert result["source_format"] == "viewpoint_text"
        # Skeleton may parse the FL/HC ratio
        assert isinstance(result["ratios"], list)

    def test_no_ratios_in_text(self):
        """Test handling when no ratios are found."""
        text = "Fetal Biometry\nHC 250 mm"

        result = parse_fetal_ratios(text, "viewpoint_text")

        assert result["ratios"] == []


# ---------------------------------------------------------------------
# ViewPoint HL7 (Skeleton)
# ---------------------------------------------------------------------


class TestFetalRatiosViewPointHL7:
    def test_skeleton_returns_empty(self):
        """Test that HL7 skeleton returns empty result."""
        hl7 = "MSH|...\nOBX|..."

        result = parse_fetal_ratios(hl7, "viewpoint_hl7")

        assert result["source_format"] == "viewpoint_hl7"
        assert result["ratios"] == []


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------


class TestFetalRatiosEdgeCases:
    def test_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            parse_fetal_ratios("data", "invalid_format")

    def test_non_string_viewpoint_text(self):
        """Test that non-string viewpoint_text raises ValueError."""
        with pytest.raises(ValueError):
            parse_fetal_ratios({"not": "string"}, "viewpoint_text")

    def test_non_string_viewpoint_hl7(self):
        """Test that non-string viewpoint_hl7 raises ValueError."""
        with pytest.raises(ValueError):
            parse_fetal_ratios({"not": "string"}, "viewpoint_hl7")

    def test_malformed_range_string(self):
        """Test handling of malformed range string."""
        data = {
            "fetuses": [
                {"ratios": [{"label": "HC/AC", "value": 1.1, "range": "invalid"}]}
            ]
        }

        result = parse_fetal_ratios(data, "observer_json")

        assert result["ratios"][0]["expected_range"] is None

    def test_integer_ratio_value(self):
        """Test that integer ratio values are handled."""
        data = {
            "fetuses": [
                {"ratios": [{"label": "FL/BPD", "value": 75, "range": "71 - 87"}]}
            ]
        }

        result = parse_fetal_ratios(data, "observer_json")

        assert result["ratios"][0]["value"] == 75
        assert result["ratios"][0]["within_range"] is True
