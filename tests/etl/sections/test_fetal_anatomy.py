"""Tests for fetal anatomy section parser."""

import json
from pathlib import Path

import pytest

from prenatalppkt.etl.sections.fetal_anatomy import parse_fetal_anatomy

HL7_ANATOMY_TEST_FILE = (
    Path(__file__).parent.parent.parent / "data" / "viewpoint_hl7_anatomy_test.txt"
)
APPLE_SALLY_FIXTURE = (
    Path(__file__).parent.parent.parent / "data" / "Apple_Sally_pretty.json"
)


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


class TestFetalAnatomyObserver:
    def test_basic_anatomy_structures(self):
        """Test parsing of normal/abnormal/unseen structures."""
        data = {
            "fetuses": [
                {
                    "fetus": {"anatomy_text": "The fetal anatomy was assessed."},
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
                    "fetus": {"anatomy_text": ""},
                    "anatomy": [
                        {
                            "main": {"label": "Head", "anat_state": "Abnormal"},
                            "detail": [
                                {"label": "Cerebellum", "anat_det_state": "Abnormal"}
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
                        "anatomy_text": "Findings consistent with Dandy-Walker malformation."
                    },
                    "anatomy": [
                        {
                            "main": {"label": "Brain", "anat_state": "Abnormal"},
                            "detail": [],
                            "anomalies": [{"description": "Ventriculomegaly noted"}],
                        }
                    ],
                }
            ]
        }

        result = parse_fetal_anatomy(data, "observer_json", hpo_cr=hpo_cr)

        hpo_ids = [t.hpo_id for t in result["hpo_terms"]]
        assert "HP:0002119" in hpo_ids  # Ventriculomegaly, from the anomaly description

    @pytest.mark.xfail(
        reason=(
            "fenominal does not recognize 'Dandy-Walker malformation' in "
            "free text, even though that phrase is an exact match for "
            "HP:0001305's official HPO label - confirmed via direct "
            "testing across several phrasings, not yet "
            "reported upstream to fenominal. This used to be masked by "
            "an 'or' fallback in test_anatomy_with_hpo_extraction above; "
            "documenting it honestly here instead. Remove this xfail once "
            "fenominal (or a fallback) recognizes the phrase."
        ),
        strict=True,
    )
    def test_dandy_walker_malformation_recognized_in_anatomy_text(self, hpo_cr):
        """Known gap, not a hidden bug: a real, present, exact-label-match
        finding is silently dropped by fenominal today."""
        data = {
            "fetuses": [
                {
                    "fetus": {
                        "anatomy_text": "Findings consistent with Dandy-Walker malformation."
                    },
                    "anatomy": [],
                }
            ]
        }

        result = parse_fetal_anatomy(data, "observer_json", hpo_cr=hpo_cr)

        hpo_ids = [t.hpo_id for t in result["hpo_terms"]]
        assert "HP:0001305" in hpo_ids

    def test_anatomy_json_string_input(self):
        """Test that JSON string input is handled correctly."""
        data = json.dumps(
            {
                "fetuses": [
                    {
                        "fetus": {"anatomy_text": "Normal anatomy."},
                        "anatomy": [
                            {"main": {"label": "Face", "anat_state": "Normal"}}
                        ],
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

    def test_real_fixture_structured_anatomy_is_populated(self):
        """The structured anatomy array lives at fetuses[i]["anatomy"], a
        sibling of "fetus" - not nested inside it. Apple Sally's real
        fixture has 16 anatomy items; this must classify them, not come
        back empty."""
        data = json.loads(APPLE_SALLY_FIXTURE.read_text())

        result = parse_fetal_anatomy(data, "observer_json")

        assert "Head" in result["abnormal_structures"]
        assert "Cerebellum" in result["abnormal_structures"]
        assert any(a["description"] == "Dandy Walker" for a in result["anomalies"])
        assert result["normal_structures"], "expected normal structures to be found"


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
# ViewPoint HL7
# ---------------------------------------------------------------------


class TestFetalAnatomyViewPointHL7:
    def test_unmatched_hl7_returns_empty(self):
        """Non-anatomy HL7 content yields empty structures, not an error."""
        hl7 = "MSH|...\nOBX|..."

        result = parse_fetal_anatomy(hl7, "viewpoint_hl7")

        assert result["source_format"] == "viewpoint_hl7"
        assert result["normal_structures"] == []
        assert result["anatomy_text"] == ""

    def test_real_field_names_classify_correctly(self):
        """
        16 real Appearance/Details fields, confirmed via the data
        dictionary (comparison.csv built from real EVMS HL7 exports) -
        not guessed. Fixture mixes normal/abnormal/suboptimal states plus
        2 Details fields.
        """
        data = HL7_ANATOMY_TEST_FILE.read_text()
        result = parse_fetal_anatomy(data, "viewpoint_hl7")

        assert set(result["normal_structures"]) == {
            "Brain",
            "Left lateral ventricle",
            "Face",
            "Chest",
            "Spine",
            "Bladder",
            "Left kidney",
        }
        assert set(result["abnormal_structures"]) == {
            "Cerebellum",
            "Gastrointestinal tract",
            "Urogenital tract",
            "Right kidney",
        }
        assert result["not_visualized"] == ["Right lateral ventricle"]

    def test_details_fields_become_anomalies(self):
        data = HL7_ANATOMY_TEST_FILE.read_text()
        result = parse_fetal_anatomy(data, "viewpoint_hl7")

        assert len(result["anomalies"]) == 2
        by_structure = {a["structure"]: a["description"] for a in result["anomalies"]}
        assert by_structure["Cerebellum"] == "cerebellar hypoplasia"
        assert by_structure["Thoracic descending aorta"] == "mild aortic arch narrowing"
        assert all(a["variant_type"] == "Abnormal" for a in result["anomalies"])

    def test_suboptimal_maps_to_not_visualized(self):
        """Open item resolved: "suboptimal" (visualization quality) maps
        to Unseen, not treated as a normal/abnormal finding."""
        data = HL7_ANATOMY_TEST_FILE.read_text()
        result = parse_fetal_anatomy(data, "viewpoint_hl7")

        assert "Right lateral ventricle" in result["not_visualized"]
        assert "Right lateral ventricle" not in result["normal_structures"]
        assert "Right lateral ventricle" not in result["abnormal_structures"]

    def test_hpo_terms_extracted_from_details_fields(self, hpo_cr):
        """The fixture has two Details findings - only 'cerebellar
        hypoplasia' is checked here since fenominal reliably recognizes
        it. See test_aortic_arch_narrowing_recognized_from_details_field
        below for the other one, which is a known gap."""
        data = HL7_ANATOMY_TEST_FILE.read_text()
        result = parse_fetal_anatomy(data, "viewpoint_hl7", hpo_cr=hpo_cr)

        hpo_ids = [t.hpo_id for t in result["hpo_terms"]]
        assert all(t.hpo_id.startswith("HP:") for t in result["hpo_terms"])
        assert "HP:0001321" in hpo_ids  # Cerebellar hypoplasia

    @pytest.mark.xfail(
        reason=(
            "fenominal does not recognize 'mild aortic arch narrowing' "
            "(the fixture's ThoracicDescAortaDetails finding) as "
            "HP:0001680 Coarctation of aorta - confirmed via direct "
            "testing: fenominal correctly matches the exact "
            "label 'coarctation of the aorta', but 'narrowing' alone is "
            "not a recognized synonym, and this fixture's text never says "
            "'coarctation'. Not yet reported upstream. This used to be "
            "masked by a len(...) > 0 check in "
            "test_hpo_terms_extracted_from_details_fields above; "
            "documenting it honestly here instead. Remove this xfail once "
            "fenominal (or a fallback) recognizes the phrase."
        ),
        strict=True,
    )
    def test_aortic_arch_narrowing_recognized_from_details_field(self, hpo_cr):
        """Known gap, not a hidden bug: a real, present anomaly finding
        in a Details field is silently dropped by fenominal today.
        Clinically, "narrowing" of the aorta is coarctation (HP:0001680) -
        confirmed fenominal recognizes that exact label, just not the
        word "narrowing" used in this fixture's free text."""
        data = HL7_ANATOMY_TEST_FILE.read_text()
        result = parse_fetal_anatomy(data, "viewpoint_hl7", hpo_cr=hpo_cr)

        hpo_ids = [t.hpo_id for t in result["hpo_terms"]]
        assert "HP:0001680" in hpo_ids  # Coarctation of aorta

    def test_no_anatomy_text_narrative_for_hl7(self):
        """HL7 has no free-text anatomy narrative field (unlike Observer's
        anatomy_text or ViewPoint text's Impression section)."""
        data = HL7_ANATOMY_TEST_FILE.read_text()
        result = parse_fetal_anatomy(data, "viewpoint_hl7")

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
