import json
import pytest

from prenatalppkt.etl.sections.clinical_indication import parse_clinical_indication


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


class TestClinicalIndicationObserver:
    def test_basic_indication(self):
        data = json.dumps({"exam": {"indication": "Advanced maternal age, dating"}})

        result = parse_clinical_indication(data, "observer_json")

        assert "Advanced maternal age" in result["indication_text"]
        assert result["source_format"] == "observer_json"
        assert result["icd10_codes"] == []
        assert result["hpo_terms"] == []

    def test_fallback_finalize_indication(self):
        data = json.dumps(
            {"exam": {"finalize": {"indication": "Poor obstetric history"}}}
        )

        result = parse_clinical_indication(data, "observer_json")
        assert result["indication_text"] == "Poor obstetric history"

    def test_missing_indication(self):
        data = json.dumps({"exam": {}})
        result = parse_clinical_indication(data, "observer_json")
        assert result["indication_text"] == ""


# ---------------------------------------------------------------------
# ViewPoint Text
# ---------------------------------------------------------------------


class TestClinicalIndicationViewPointText:
    def test_basic_indication(self):
        text = """Indication
==========
Advanced maternal age, dating

History
=======
Previous cesarean section
"""
        result = parse_clinical_indication(text, "viewpoint_text")

        assert "Advanced maternal age" in result["indication_text"]
        assert "History" not in result["indication_text"]
        assert result["source_format"] == "viewpoint_text"

    def test_multiline_indication(self):
        text = """Indication
==========
Advanced maternal age
Previous cesarean section
IVF pregnancy
"""
        result = parse_clinical_indication(text, "viewpoint_text")

        assert "IVF pregnancy" in result["indication_text"]
        assert result["indication_text"].count("\n") >= 1

    def test_missing_indication_section(self):
        text = """Fetal Biometry
============
HC 175.0 mm
"""
        result = parse_clinical_indication(text, "viewpoint_text")
        assert result["indication_text"] == ""


# ---------------------------------------------------------------------
# ViewPoint HL7
# ---------------------------------------------------------------------


class TestClinicalIndicationViewPointHL7:
    def test_basic_indication(self):
        hl7 = (
            "MSH|^~\\&|\n"
            "OBX||ST|RequestedProcedure.Indication^Indication|1|Advanced maternal age\n"
            "OBX||ST|RequestedProcedure.Indication^Indication|2|Dating scan\n"
        )

        result = parse_clinical_indication(hl7, "viewpoint_hl7")

        assert "Advanced maternal age" in result["indication_text"]
        assert "Dating scan" in result["indication_text"]
        assert result["source_format"] == "viewpoint_hl7"

    def test_no_indication_obx(self):
        hl7 = "MSH|^~\\&|\nOBX||NM|SomeOtherField|1|123\n"
        result = parse_clinical_indication(hl7, "viewpoint_hl7")
        assert result["indication_text"] == ""


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------


class TestClinicalIndicationEdgeCases:
    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_clinical_indication("data", "unknown_format")

    def test_non_string_text(self):
        with pytest.raises(ValueError):
            parse_clinical_indication({"bad": "data"}, "viewpoint_text")

    def test_special_characters(self):
        text = """Indication
==========
Advanced maternal age - >=35 years
"""
        result = parse_clinical_indication(text, "viewpoint_text")
        assert ">=35" in result["indication_text"]
