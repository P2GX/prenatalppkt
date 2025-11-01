from fasthpocr import FastHPOCR

class PhenotypeMiner:
    def __init__(self):
        self.recogniser = FastHPOCR()

    def extract_phenotypes(self, text: str) -> list[dict]:
        # For each text, get recognised phenotypes
        matches = self.recogniser.recognise(text)
        # Maybe convert matches to a simpler form
        return [{"term": m["term"], "hpo_id": m["hpo_id"], "span": m["span"]} for m in matches]

    def analyse_texts(self, texts: list[str]) -> list:
        result = []
        for t in texts:
            pheno = self.extract_phenotypes(t)
            result.append({"text": t, "phenotypes": pheno})
        return result
