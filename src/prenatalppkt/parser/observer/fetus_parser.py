from pyphetools.creation import HpoParser, HpoConceptRecognizer

class FetusParser:
    def __init__ (self, hcr: HpoConceptRecognizer):
        self._hcr = hcr
    
    def parse (self, json_data: typing.Dict[str, object]) -> FetusData:
        if not isinstance(json_data, dict):
            raise ValueError(f"malformed arguement, expecting `dict` but got {type(json_data)}")
    
        if "patient" not in json_data:
            raise ValueError(f"did not find 'patient' in exam")

        patient = json_data.get("patient")

        first_name = patient.get('first_name', "NA")
        last_name = patient.get('last_name', "NA")
