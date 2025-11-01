import typing
from prenatalppkt.hpo import HpoConceptRecognizer
from prenatalppkt.dto import FetusData

class FetusParser:
    def __init__ (self, hcr: HpoConceptRecognizer):
        self._hcr = hcr
    
    def parse (self, json_data: typing.Dict[str, object]) -> FetusData:
        if not isinstance(json_data, dict):
            raise ValueError(f"malformed arguement, expecting `dict` but got {type(json_data)}")
    
        if "anatomy_text" not in json_data:
            raise ValueError(f"did not find 'anatomy_text' in fetus")

        anatomy_text = json_data.get("anatomy_text")

        #first_name = patient.get('first_name', "NA")
        for hpo_hit in self._hcr.parse(anatomy_text):
            print(hpo_hit)