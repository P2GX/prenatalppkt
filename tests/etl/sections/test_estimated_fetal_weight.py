"""Tests for estimated fetal weight section parser."""

import json
import pytest

from prenatalppkt.etl.sections.estimated_fetal_weight import (
    parse_estimated_fetal_weight,
)


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


class TestEstimatedFetalWeightObserver:
    def test_basic_efw(self):
        """Test parsing of basic EFW data."""
        data = {
            "fetuses": [
                {
                    "efws": [
                        {
                            "fetus_number": 1,
                            "label": "EFW (AC, FL, HC)",
                            "value": 1014.828,
                            "calculated_percentile": 55.6,
                            "percentile_for_display": "56%",
                            "print_in_report": 1,
                        }
                    ]
                }
            ]
        }

        result = parse_estimated_fetal_weight(data, "observer_json")

        assert result["efw_grams"] == 1014.8
        assert result["percentile"] == 55.6
        assert result["method"] == "Hadlock (AC, FL, HC)"
        assert result["within_normal_range"] is True
        assert result["growth_category"] == "AGA"
        assert result["source_format"] == "observer_json"

    def test_multiple_efw_estimates(self):
        """Test that primary EFW is selected correctly."""
        data = {
            "fetuses": [
                {
                    "efws": [
                        {
                            "label": "EFW (AC, FL, HC)",
                            "value": 1014.828,
                            "calculated_percentile": 55.6,
                            "print_in_report": 1,
                        },
                        {
                            "label": "EFW (AC, FL)",
                            "value": 1042.214,
                            "calculated_percentile": 63.7,
                            "print_in_report": 0,
                        },
                        {
                            "label": "EFW (AC, BPD)",
                            "value": 1000.887,
                            "calculated_percentile": 51.2,
                            "print_in_report": 0,
                        },
                    ]
                }
            ]
        }

        result = parse_estimated_fetal_weight(data, "observer_json")

        # Should select the one with print_in_report=1
        assert result["efw_grams"] == 1014.8
        assert len(result["all_estimates"]) == 3

    def test_sga_classification(self):
        """Test SGA (Small for Gestational Age) classification."""
        data = {
            "fetuses": [
                {
                    "efws": [
                        {
                            "label": "EFW (AC, FL, HC)",
                            "value": 800.0,
                            "calculated_percentile": 5.0,
                            "print_in_report": 1,
                        }
                    ]
                }
            ]
        }

        result = parse_estimated_fetal_weight(data, "observer_json")

        assert result["growth_category"] == "SGA"
        assert result["within_normal_range"] is False

    def test_lga_classification(self):
        """Test LGA (Large for Gestational Age) classification."""
        data = {
            "fetuses": [
                {
                    "efws": [
                        {
                            "label": "EFW (AC, FL, HC)",
                            "value": 2500.0,
                            "calculated_percentile": 95.0,
                            "print_in_report": 1,
                        }
                    ]
                }
            ]
        }

        result = parse_estimated_fetal_weight(data, "observer_json")

        assert result["growth_category"] == "LGA"
        assert result["within_normal_range"] is False

    def test_json_string_input(self):
        """Test that JSON string input is handled correctly."""
        data = json.dumps(
            {
                "fetuses": [
                    {
                        "efws": [
                            {
                                "label": "EFW (AC, FL)",
                                "value": 1200.0,
                                "calculated_percentile": 50.0,
                                "print_in_report": 1,
                            }
                        ]
                    }
                ]
            }
        )

        result = parse_estimated_fetal_weight(data, "observer_json")

        assert result["efw_grams"] == 1200.0

    def test_empty_fetuses(self):
        """Test handling of empty fetuses array."""
        data = {"fetuses": []}

        result = parse_estimated_fetal_weight(data, "observer_json")

        assert result["efw_grams"] is None
        assert result["all_estimates"] == []

    def test_missing_efws_key(self):
        """Test handling of fetus without efws key."""
        data = {"fetuses": [{"fetus": {}}]}

        result = parse_estimated_fetal_weight(data, "observer_json")

        assert result["efw_grams"] is None

    def test_fallback_to_first_estimate(self):
        """Test fallback when no estimate has print_in_report=1."""
        data = {
            "fetuses": [
                {
                    "efws": [
                        {
                            "label": "EFW (AC, FL)",
                            "value": 1100.0,
                            "calculated_percentile": 45.0,
                            "print_in_report": 0,
                        },
                        {
                            "label": "EFW (AC, BPD)",
                            "value": 1050.0,
                            "calculated_percentile": 40.0,
                            "print_in_report": 0,
                        },
                    ]
                }
            ]
        }

        result = parse_estimated_fetal_weight(data, "observer_json")

        # Should fall back to first estimate
        assert result["efw_grams"] == 1100.0


# ---------------------------------------------------------------------
# ViewPoint Text (Skeleton)
# ---------------------------------------------------------------------


class TestEstimatedFetalWeightViewPointText:
    def test_skeleton_returns_structure(self):
        """Test that skeleton implementation returns expected structure."""
        text = "EFW   2,042   g   2%\nEFW by   Hadlock"

        result = parse_estimated_fetal_weight(text, "viewpoint_text")

        assert result["source_format"] == "viewpoint_text"
        # Skeleton may parse basic patterns
        assert isinstance(result["all_estimates"], list)

    def test_no_efw_in_text(self):
        """Test handling when no EFW is found."""
        text = "Fetal Biometry\nHC 250 mm"

        result = parse_estimated_fetal_weight(text, "viewpoint_text")

        assert result["efw_grams"] is None


# ---------------------------------------------------------------------
# ViewPoint HL7 (Skeleton)
# ---------------------------------------------------------------------


class TestEstimatedFetalWeightViewPointHL7:
    def test_skeleton_returns_empty(self):
        """Test that HL7 skeleton returns empty result."""
        hl7 = "MSH|...\nOBX|..."

        result = parse_estimated_fetal_weight(hl7, "viewpoint_hl7")

        assert result["source_format"] == "viewpoint_hl7"
        assert result["efw_grams"] is None


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------


class TestEstimatedFetalWeightEdgeCases:
    def test_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            parse_estimated_fetal_weight("data", "invalid_format")

    def test_non_string_viewpoint_text(self):
        """Test that non-string viewpoint_text raises ValueError."""
        with pytest.raises(ValueError):
            parse_estimated_fetal_weight({"not": "string"}, "viewpoint_text")

    def test_non_string_viewpoint_hl7(self):
        """Test that non-string viewpoint_hl7 raises ValueError."""
        with pytest.raises(ValueError):
            parse_estimated_fetal_weight({"not": "string"}, "viewpoint_hl7")

    def test_boundary_aga_at_10_percentile(self):
        """Test AGA classification at exactly 10th percentile."""
        data = {
            "fetuses": [
                {
                    "efws": [
                        {
                            "label": "EFW",
                            "value": 900.0,
                            "calculated_percentile": 10.0,
                            "print_in_report": 1,
                        }
                    ]
                }
            ]
        }

        result = parse_estimated_fetal_weight(data, "observer_json")
        assert result["growth_category"] == "AGA"
        assert result["within_normal_range"] is True

    def test_boundary_aga_at_90_percentile(self):
        """Test AGA classification at exactly 90th percentile."""
        data = {
            "fetuses": [
                {
                    "efws": [
                        {
                            "label": "EFW",
                            "value": 2000.0,
                            "calculated_percentile": 90.0,
                            "print_in_report": 1,
                        }
                    ]
                }
            ]
        }

        result = parse_estimated_fetal_weight(data, "observer_json")
        assert result["growth_category"] == "AGA"
        assert result["within_normal_range"] is True
