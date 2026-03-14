import json
import pytest

from prenatalppkt.etl.sections.pregnancy_dating import parse_pregnancy_dating


# ---------------------------------------------------------------------
# Observer JSON
# ---------------------------------------------------------------------


class TestPregnancyDatingObserver:
    def test_basic_lmp_and_edd(self):
        data = json.dumps(
            {"exam": {"lmp": "2025-01-15", "edd": "2025-10-22", "dating_method": "LMP"}}
        )

        result = parse_pregnancy_dating(data, "observer_json")

        assert result["lmp"] == "2025-01-15"
        assert result["edd"] == "2025-10-22"
        assert result["ga_by_lmp"] is None
        assert result["source_format"] == "observer_json"

    def test_missing_dates(self):
        data = json.dumps({"exam": {}})
        result = parse_pregnancy_dating(data, "observer_json")
        assert result["lmp"] is None
        assert result["ga_by_lmp"] is None


# ---------------------------------------------------------------------
# ViewPoint Text
# ---------------------------------------------------------------------


class TestPregnancyDatingViewPointText:
    def test_basic_dating_section(self):
        text = """Dating
======
LMP 01/15/2025
EDD by LMP 10/22/2025
Assigned dating based on LMP
"""

        result = parse_pregnancy_dating(text, "viewpoint_text")

        assert result["lmp"] == "2025-01-15"
        assert result["edd"] == "2025-10-22"
        assert result["ga_by_lmp"] is None
        assert "Assigned" in result["dating_method"]

    def test_missing_dating_section(self):
        text = "Fetal Biometry\n============\nHC 175 mm"
        result = parse_pregnancy_dating(text, "viewpoint_text")
        assert result["lmp"] is None
        assert result["edd"] is None


# ---------------------------------------------------------------------
# ViewPoint HL7
# ---------------------------------------------------------------------


class TestPregnancyDatingViewPointHL7:
    def test_basic_hl7_dates(self):
        hl7 = (
            "OBX||DT|EpisodeHistory.LastMenstrualPeriod^LMP|1|20250115\n"
            "OBX||DT|EpisodeHistory.EDDbyLMP^EDD|1|20251022\n"
        )

        result = parse_pregnancy_dating(hl7, "viewpoint_hl7")

        assert result["lmp"] == "2025-01-15"
        assert result["edd"] == "2025-10-22"
        assert result["ga_by_lmp"] is None

    def test_no_dates(self):
        hl7 = "OBX||NM|SomeOtherField|1|123\n"
        result = parse_pregnancy_dating(hl7, "viewpoint_hl7")
        assert result["lmp"] is None
        assert result["ga_by_lmp"] is None


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------


class TestPregnancyDatingEdgeCases:
    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_pregnancy_dating("data", "bad_format")

    def test_non_string_text(self):
        with pytest.raises(ValueError):
            parse_pregnancy_dating({"bad": "data"}, "viewpoint_text")

    def test_malformed_dates(self):
        text = """Dating
        ======
        LMP not-a-date
        """
        result = parse_pregnancy_dating(text, "viewpoint_text")
        assert result["lmp"] is None
        assert result["ga_by_lmp"] is None
