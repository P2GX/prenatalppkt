import json
import pytest

from prenatalppkt.etl.sections.clinical_impression import parse_clinical_impression


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


class TestClinicalImpressionObserver:
    def test_basic_impression(self, hpo_cr):
        data = json.dumps(
            {
                "exam": {
                    "finalize": {
                        "generalComment": {
                            "plain_text": "Normal fetal anatomy. No abnormalities."
                        }
                    }
                }
            }
        )

        result = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)

        assert "Normal fetal anatomy" in result["impression_text"]
        assert result["hpo_terms"] == []
        assert result["source_format"] == "observer_json"


# ---------------------------------------------------------------------
# ViewPoint Text
# ---------------------------------------------------------------------


class TestClinicalImpressionViewPointText:
    def test_basic_impression(self, hpo_cr):
        text = """Impression
=========
Fetal growth restriction is suspected.
Recommend follow-up scan.
"""

        result = parse_clinical_impression(text, "viewpoint_text", hpo_cr=hpo_cr)

        assert "growth restriction" in result["impression_text"].lower()
        assert result["growth_assessment"] == "FGR"
        assert isinstance(result["hpo_terms"], list)

    def test_missing_impression(self, hpo_cr):
        text = "Fetal Biometry\n============\nHC 175 mm"
        result = parse_clinical_impression(text, "viewpoint_text", hpo_cr=hpo_cr)
        assert result["impression_text"] == ""


# ---------------------------------------------------------------------
# ViewPoint HL7
# ---------------------------------------------------------------------


class TestClinicalImpressionViewPointHL7:
    def test_basic_hl7_impression(self, hpo_cr):
        hl7 = "OBX||TX|Impression^Impression|1|Appropriate for gestational age\n"

        result = parse_clinical_impression(hl7, "viewpoint_hl7", hpo_cr=hpo_cr)

        assert "Appropriate" in result["impression_text"]
        assert result["growth_assessment"] == "AGA"


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------


class TestClinicalImpressionEdgeCases:
    def test_invalid_format(self, hpo_cr):
        with pytest.raises(ValueError):
            parse_clinical_impression("data", "bad_format", hpo_cr=hpo_cr)

    def test_non_string_text(self, hpo_cr):
        with pytest.raises(ValueError):
            parse_clinical_impression({"bad": "data"}, "viewpoint_text", hpo_cr=hpo_cr)
