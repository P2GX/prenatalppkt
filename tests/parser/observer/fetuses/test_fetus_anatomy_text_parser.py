from prenatalppkt.parser.observer.fetuses.fetuses_anatomy_text_parser import (
    FetusAnatomyTextParser,
)


class DummyHPO:
    """Mock HPO parser for testing"""

    def parse(self, text):
        return []


def test_parse_anatomy_text_basic():
    parser = FetusAnatomyTextParser(DummyHPO())
    json_data = {"anatomy_text": "There was a neural tube defect."}
    result = parser.parse(json_data)
    assert "hpo_hits" in result
    assert isinstance(result["hpo_hits"], list)
