from prenatalppkt.hpo import HpoParser

class PhenotypeMiner:
    """
    Use the local HPO ontology to recognize phenotype terms in free text.
    """

    def __init__(self, hpo_json: str | None = None, release: str | None = None):
        self._hpo = HpoParser(hpo_json_file=hpo_json, release=release)
        self._hcr = self._hpo.get_hpo_concept_recognizer()

    def extract_phenotypes(self, text: str) -> list[dict]:
        if not isinstance(text, str) or not text.strip():
            return []
        matches = self._hcr.parse(text)
        return [
            {"term": m.hpo_label, "hpo_id": m.hpo_id}
            for m in matches
        ]

    def analyse_texts(self, texts: list[str]) -> list[dict]:
        result = []
        for t in texts:
            phenos = self.extract_phenotypes(t)
            result.append({"text": t, "phenotypes": phenos})
        return result
