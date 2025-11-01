import typing
from prenatalppkt.hpo import HpoConceptRecognizer

"""
for the "fetus" subfield in the "fetus" superfield within the Observer JSON
"""


class FetusFetusParser:
    def __init__(self, hcr: HpoConceptRecognizer):
        self._hcr = hcr

    def parse(self, json_data: typing.Dict[str, object]) -> typing.Dict[str, object]:
        if not isinstance(json_data, dict):
            raise ValueError(
                f"malformed arguement, expecting `dict` but got {type(json_data)}"
            )

        values = dict()

        if "anatomy_text" not in json_data:
            raise ValueError("did not find 'anatomy_text' in fetus")
        anatomy_text = json_data.get("anatomy_text")
        hpo_hits = self._hcr.parse(anatomy_text)

        values["hpo_hits"] = hpo_hits

        return values
