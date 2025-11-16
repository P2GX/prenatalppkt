import typing
import re


class ViewpointImpressionParser:
    """
    Parse free-text from the Clinical Impressions section

    Raises:
        ValueError: _description_
    """

    # Any sentence ending in ., !, or ?
    # SENTENCE_END = re.compile(r".*[.!?]$")
    SENTENCE_END = re.compile(r".*(?<=[^\.])\.$|.*[!?]$")

    def __init__(self, lines: typing.List[str], hpo_cr=None):
        # Remove blank or whitespace-only lines
        raw_impression_text = [line.strip() for line in lines if line.strip()]

        impression_sentences: typing.List[str] = []
        current_line: typing.List[str] = []

        self.hpo_cr = hpo_cr

        # Build sentences from lines
        for line in raw_impression_text:
            current_line.append(line)
            joined_sentence = " ".join(current_line)

            # If we found a complete sentence, store it
            # Sentence ends ONLY if the *current line* ends with a real terminator
            if self.SENTENCE_END.match(line):
                impression_sentences.append(joined_sentence)
                current_line = []

        # If there's leftover sentence material at end of block
        if current_line:
            impression_sentences.append(" ".join(current_line))

        self.paragraphs = impression_sentences
        self.impression = " ".join(impression_sentences)

        if not self.impression:
            raise ValueError(
                f"Did not understand impression lines in {raw_impression_text}"
            )

        cr = self.hpo_cr

        # Dict: sentence_index → list[SimpleTerm]
        self.hpo_by_sentence: dict[int, list] = {}

        if cr:
            for index, sent in enumerate(self.paragraphs, start=1):
                self.hpo_by_sentence[index] = cr.find_concepts(sent)
        else:
            for index, sent in enumerate(self.paragraphs, start=1):
                self.hpo_by_sentence[index] = []

        # Flat list of all HPO terms
        all_terms: list = []
        if cr:
            for terms in self.hpo_by_sentence.values():
                all_terms.extend(terms)

        self.hpo_terms = all_terms
