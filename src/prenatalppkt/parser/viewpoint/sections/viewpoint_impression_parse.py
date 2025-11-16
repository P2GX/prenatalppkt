import typing
import re


class ViewpointImpressionParser:
    """
    Parse free-text from the Clinical Impressions section

    Raises:
        ValueError: _description_
    """

    # Any sentence ending in ., !, or ?
    SENTENCE_END = re.compile(r".*[.!?]$")

    def __init__(self, lines: typing.List[str]):
        # Remove blank or whitespace-only lines
        raw_impression_text = [line.strip() for line in lines if line.strip()]

        impression_sentences: typing.List[str] = []
        current_line: typing.List[str] = []

        # Build sentences from lines
        for line in raw_impression_text:
            current_line.append(line)
            joined_sentence = " ".join(current_line)

            # If we found a complete sentence, store it
            if self.SENTENCE_END.match(joined_sentence):
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
