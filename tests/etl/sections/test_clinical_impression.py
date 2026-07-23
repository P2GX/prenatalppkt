import json
from pathlib import Path

import pytest

from prenatalppkt.etl.sections.clinical_impression import parse_clinical_impression

DATA_DIR = Path(__file__).parent.parent.parent / "data"


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
# Real Observer fixtures - ground truth confirmed by hand 2026-07-21
# against each fixture's real impression text. Section-parser-level
# companions to the builder-level tests in
# tests/builders/test_observer_phenopacket.py.
# ---------------------------------------------------------------------


class TestClinicalImpressionRealFixtures:
    def test_blue_sally_clean_findings(self, hpo_cr):
        """The two findings that DO get recognized correctly."""
        data = json.loads((DATA_DIR / "Blue_Sally_pretty.json").read_text())

        result = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)

        hpo_ids = {t.hpo_id for t in result["hpo_terms"]}
        assert "HP:0000122" in hpo_ids  # Unilateral renal agenesis
        assert "HP:0000813" in hpo_ids  # Bicornuate uterus

    @pytest.mark.xfail(
        reason=(
            "Known fenominal gap: the text says 'possible unicornuate or "
            "bicornuate uterus' - only 'bicornuate' is recognized. "
            "'unicornuate uterus' tested alone IS recognized as "
            "HP:0031909, so it's specifically the combined sentence that "
            "defeats recognition. Confirmed 2026-07-21; see the matching "
            "builder-level test in test_observer_phenopacket.py. Remove "
            "once fenominal (or a fallback) recognizes the phrase in "
            "context."
        ),
        strict=True,
    )
    def test_blue_sally_unicornuate_uterus(self, hpo_cr):
        """Known gap, not a hidden bug."""
        data = json.loads((DATA_DIR / "Blue_Sally_pretty.json").read_text())

        result = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)

        hpo_ids = {t.hpo_id for t in result["hpo_terms"]}
        assert "HP:0031909" in hpo_ids  # Unicornuate uterus

    def test_charm_sally_clean_findings(self, hpo_cr):
        """Both real findings correctly recognized, no known gap here."""
        data = json.loads((DATA_DIR / "Charm_Sally_pretty.json").read_text())

        result = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)

        hpo_ids = {t.hpo_id for t in result["hpo_terms"]}
        assert "HP:0010866" in hpo_ids  # Abdominal wall defect
        assert "HP:0001539" in hpo_ids  # Omphalocele

    def test_diva_sally_clean_findings(self, hpo_cr):
        """The one real finding correctly recognized, no known gap here."""
        data = json.loads((DATA_DIR / "Diva_Sally_pretty.json").read_text())

        result = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)

        hpo_ids = {t.hpo_id for t in result["hpo_terms"]}
        assert "HP:0030716" in hpo_ids  # Acrania

    def test_eclair_sally_clean_finding(self, hpo_cr):
        """The generic parent term that DOES get recognized correctly."""
        data = json.loads((DATA_DIR / "Eclair_Sally_pretty.json").read_text())

        result = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)

        hpo_ids = {t.hpo_id for t in result["hpo_terms"]}
        assert "HP:0001627" in hpo_ids  # Abnormal heart morphology

    @pytest.mark.xfail(
        reason=(
            "Known fenominal gap: the text describes 'a small ascending "
            "aorta, and a small but thick-walled left ventricle and "
            "enlarged right heart chambers' - only the generic 'Abnormal "
            "heart morphology' parent term survives. 'Cardiomegaly' "
            "tested alone (the closest match for 'enlarged...chambers') "
            "IS recognized, so it's the full-sentence context that "
            "defeats recognition, not missing vocabulary. Confirmed "
            "2026-07-21; see the matching builder-level test in "
            "test_observer_phenopacket.py. Remove once fenominal (or a "
            "fallback) recognizes the phrase in context."
        ),
        strict=True,
    )
    def test_eclair_sally_right_heart_finding(self, hpo_cr):
        """Known gap, not a hidden bug."""
        data = json.loads((DATA_DIR / "Eclair_Sally_pretty.json").read_text())

        result = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)

        hpo_ids = {t.hpo_id for t in result["hpo_terms"]}
        assert "HP:0001640" in hpo_ids  # Cardiomegaly


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
