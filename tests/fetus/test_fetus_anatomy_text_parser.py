from prenatalppkt.parser.observer.fetus.fetus_anatomy_text_parser import (
    FetusAnatomyTextParser,
)


class DummyHPO:
    def parse(self, text):
        return (
            [{"hpo_label": "Neural tube defect"}]
            if "neural tube defect" in text.lower()
            else []
        )


def test_parse_anatomy_text_basic():
    parser = FetusAnatomyTextParser(DummyHPO())
    json_data = {"anatomy_text": "There was a neural tube defect."}
    result = parser.parse(json_data)
    assert len(result.hpo_term_list) == 1
    assert result.hpo_term_list[0]["hpo_label"] == "Neural tube defect"
