"""Tests for fetal anatomy section parser."""

import json
import pytest

from prenatalppkt.etl.sections.fetal_anatomy import parse_fetal_anatomy


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


class TestFetalAnatomyObserver:
    def test_basic_anatomy_structures(self):
        """Test parsing of normal/abnormal/unseen structures."""
        data = {
            "fetuses": [
                {
                    "fetus": {
                        "anatomy_text": "The fetal anatomy was assessed.",
                        "anatomy": [
                            {
                                "main": {"label": "Head", "anat_state": "Normal"},
                                "detail": [],
                                "anomalies": [],
                            },
                            {
                                "main": {"label": "Heart", "anat_state": "Abnormal"},
                                "detail": [],
                                "anomalies": [],
                            },
                            {
                                "main": {"label": "Spine", "anat_state": "Unseen"},
                                "detail": [],
                                "anomalies": [],
                            },
                        ],
                    }
                }
            ]
        }

        result = parse_fetal_anatomy(data, "observer_json")

        assert "Head" in result["normal_structures"]
        assert "Heart" in result["abnormal_structures"]
        assert "Spine" in result["not_visualized"]
        assert result["anatomy_text"] == "The fetal anatomy was assessed."
        assert result["source_format"] == "observer_json"

    def test_anatomy_with_anomalies(self):
        """Test parsing of specific anomaly descriptions."""
        data = {
            "fetuses": [
                {
                    "fetus": {
                        "anatomy_text": "",
                        "anatomy": [
                            {
                                "main": {"label": "Head", "anat_state": "Abnormal"},
                                "detail": [
                                    {
                                        "label": "Cerebellum",
                                        "anat_det_state": "Abnormal",
                                    }
                                ],
                                "anomalies": [
                                    {
                                        "description": "Dandy Walker",
                                        "abnormal_or_normal_variant": "Abnormal",
                                    }
                                ],
                            }
                        ],
                    }
                }
            ]
        }

        result = parse_fetal_anatomy(data, "observer_json")

        assert "Head" in result["abnormal_structures"]
        assert "Cerebellum" in result["abnormal_structures"]
        assert len(result["anomalies"]) == 1
        assert result["anomalies"][0]["structure"] == "Head"
        assert result["anomalies"][0]["description"] == "Dandy Walker"
        assert result["anomalies"][0]["variant_type"] == "Abnormal"

    def test_anatomy_with_hpo_extraction(self, hpo_cr):
        """Test HPO term extraction from anomaly descriptions."""
        data = {
            "fetuses": [
                {
                    "fetus": {
                        "anatomy_text": "Findings consistent with Dandy-Walker malformation.",
                        "anatomy": [
                            {
                                "main": {"label": "Brain", "anat_state": "Abnormal"},
                                "detail": [],
                                "anomalies": [
                                    {"description": "Ventriculomegaly noted"}
                                ],
                            }
                        ],
                    }
                }
            ]
        }

        result = parse_fetal_anatomy(data, "observer_json", hpo_cr=hpo_cr)

        # Should find HPO terms from the combined text
        assert len(result["hpo_terms"]) > 0
        hpo_ids = [t.hpo_id for t in result["hpo_terms"]]
        # Dandy-Walker malformation is HP:0001305
        assert "HP:0001305" in hpo_ids or "HP:0002119" in hpo_ids  # Ventriculomegaly

    def test_anatomy_json_string_input(self):
        """Test that JSON string input is handled correctly."""
        data = json.dumps(
            {
                "fetuses": [
                    {
                        "fetus": {
                            "anatomy_text": "Normal anatomy.",
                            "anatomy": [
                                {"main": {"label": "Face", "anat_state": "Normal"}}
                            ],
                        }
                    }
                ]
            }
        )

        result = parse_fetal_anatomy(data, "observer_json")

        assert "Face" in result["normal_structures"]

    def test_empty_fetuses(self):
        """Test handling of empty fetuses array."""
        data = {"fetuses": []}

        result = parse_fetal_anatomy(data, "observer_json")

        assert result["normal_structures"] == []
        assert result["abnormal_structures"] == []
        assert result["anomalies"] == []

    def test_missing_anatomy_key(self):
        """Test handling of fetus without anatomy key."""
        data = {"fetuses": [{"fetus": {"anatomy_text": "Some text."}}]}

        result = parse_fetal_anatomy(data, "observer_json")

        assert result["anatomy_text"] == "Some text."
        assert result["normal_structures"] == []


# ---------------------------------------------------------------------
# ViewPoint Text (Skeleton)
# ---------------------------------------------------------------------


class TestFetalAnatomyViewPointText:
    def test_skeleton_returns_empty_structures(self):
        """Test that skeleton implementation returns expected structure."""
        text = """Fetal Anatomy
=============
The following structures appear normal:
Cranium. Brain. Face.
"""

        result = parse_fetal_anatomy(text, "viewpoint_text")

        assert result["source_format"] == "viewpoint_text"
        assert isinstance(result["normal_structures"], list)
        assert isinstance(result["abnormal_structures"], list)
        # Skeleton extracts anatomy_text but doesn't parse structure lists yet
        assert "normal" in result["anatomy_text"].lower()


# ---------------------------------------------------------------------
# ViewPoint HL7 (Skeleton)
# ---------------------------------------------------------------------


class TestFetalAnatomyViewPointHL7:
    def test_skeleton_returns_empty(self):
        """Test that HL7 skeleton returns empty result."""
        hl7 = "MSH|...\nOBX|..."

        result = parse_fetal_anatomy(hl7, "viewpoint_hl7")

        assert result["source_format"] == "viewpoint_hl7"
        assert result["normal_structures"] == []
        assert result["anatomy_text"] == ""


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------


class TestFetalAnatomyEdgeCases:
    def test_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            parse_fetal_anatomy("data", "invalid_format")

    def test_non_string_viewpoint_text(self):
        """Test that non-string viewpoint_text raises ValueError."""
        with pytest.raises(ValueError):
            parse_fetal_anatomy({"not": "string"}, "viewpoint_text")

    def test_non_string_viewpoint_hl7(self):
        """Test that non-string viewpoint_hl7 raises ValueError."""
        with pytest.raises(ValueError):
            parse_fetal_anatomy({"not": "string"}, "viewpoint_hl7")
