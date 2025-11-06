from prenatalppkt.dto.fetus_data import FetusData
from prenatalppkt.hpo.simple_term import SimpleTerm
from prenatalppkt.parser.observer.fetus.fetus_anatomy_text_parser import (
    FetusAnatomyTextParser,
)
import typing


class DummyHPO:
    def parse(self, text):
        return (
            [{"hpo_label": "Neural tube defect"}]
            if "neural tube defect" in text.lower()
            else []
        )


def test_parse_anatomy_text_basic(hpo_cr):
    parser = FetusAnatomyTextParser(hpo_cr)
    json_data: typing.Dict[str,object] = {"anatomy_text": "There was a neural tube defect."}
    fetusData: FetusData = parser.parse(json_data)
    hpo_term_list: typing.List[SimpleTerm] = fetusData.hpo_term_list
    assert len(hpo_term_list) == 1
    assert hpo_term_list[0].hpo_label == "Neural tube defect"
