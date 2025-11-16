from prenatalppkt.parser.observer.fetuses.fetuses_anatomy_text_parser import (
    FetusAnatomyTextParser,
)
from prenatalppkt.hpo.simple_term import SimpleTerm


class DummyHPO:
    """Mock HPO parser for testing"""

    def parse(self, text):  # Changed from parse_cell
        # Return SimpleTerm objects instead of dicts
        if "seizure" in text.lower():
            return [SimpleTerm(hpo_id="HP:0001250", hpo_label="Seizure")]
        return []


def test_parse_anatomy_text_basic():
    parser = FetusAnatomyTextParser(DummyHPO())
    json_data = {"anatomy_text": "There was a Seizure."}
    result = parser.parse(json_data)

    assert "hpo_hits" in result
    assert isinstance(result["hpo_hits"], list)
    assert len(result["hpo_hits"]) == 1
    assert isinstance(result["hpo_hits"][0], SimpleTerm)
    assert result["hpo_hits"][0].hpo_label == "Seizure"
