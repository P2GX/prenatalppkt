import typing
import re


class ViewpointImpressionParser:
    """
    Parse free-text from the Clinical Impressions section
    and extract HPO concepts via a provided recognizer.
    """

    # Ends with real punctuation, but NOT "..."
    REAL_END = re.compile(r".*(?<!\.\.)[.!?]$")

    def __init__(self, lines: typing.List[str], hpo_cr=None):
        # Store recognizer for later use
        self.hpo_cr = hpo_cr

        # Parse sentences
        sentences = self._parse_sentences(lines)
        self.paragraphs = sentences
        self.impression = " ".join(sentences)

        if not self.impression:
            raise ValueError("Did not understand impression lines")

        # Extract HPO
        self.hpo_by_sentence = self._extract_hpo(sentences)
        self.hpo_terms = [
            term for terms in self.hpo_by_sentence.values() for term in terms
        ]

    # ------------------------------------------------------------------
    # Sentence parsing
    # ------------------------------------------------------------------

    def _parse_sentences(self, lines: typing.List[str]) -> list[str]:
        """Convert raw text lines into clean, merged sentences."""
        stripped = [line.rstrip() for line in lines]

        sentences: list[str] = []
        current: list[str] = []

        for line in stripped:
            # blank line = force sentence break
            if line.strip() == "":
                if current:
                    sentences.append(" ".join(current).strip())
                    current = []
                continue

            current.append(line.strip())

            # Real sentence ending
            if self.REAL_END.match(line.strip()):
                sentences.append(" ".join(current).strip())
                current = []

        # leftover fragment
        if current:
            sentences.append(" ".join(current).strip())

        # Remove header junk
        sentences = [s for s in sentences if s not in ("Impression", "=========")]

        return sentences

    # ------------------------------------------------------------------
    # HPO Extraction
    # ------------------------------------------------------------------

    def _extract_hpo(self, sentences: list[str]) -> dict[int, list]:
        """Run HPO recognizer on each sentence."""
        result: dict[int, list] = {}

        for idx, sent in enumerate(sentences, start=1):
            if self.hpo_cr is None:
                result[idx] = []
            else:
                result[idx] = self._call_hpo_cr(self.hpo_cr, sent)
        return result

    # ------------------------------------------------------------------
    # Universal CR adapter
    # ------------------------------------------------------------------

    def _call_hpo_cr(self, cr, sent: str):
        """
        Universal adapter for ALL concept recognizers.

        Attempts every known HPO method name, then falls back
        to scanning *all* callables on the object that accept one argument
        and return a list-like value.
        """

        # Known method names used across recognizers
        method_names = [
            "find_concepts",
            "get_concepts",
            "extract",
            "find",
            "match",
            "match_terms",
            "recognize",
            "annotate",
            "concepts_from_text",
            "get_matches",
        ]

        # 1. Known standard names
        for name in method_names:
            if hasattr(cr, name):
                method = getattr(cr, name)
                try:
                    out = method(sent)
                    if isinstance(out, (list, tuple, set)):
                        return list(out)
                except Exception:
                    pass

        # 2. Fallback: try any method on the CR
        for attr in dir(cr):
            if attr.startswith("_"):
                continue
            method = getattr(cr, attr)
            if callable(method):
                try:
                    out = method(sent)
                    if isinstance(out, (list, tuple, set)):
                        return list(out)
                except Exception:
                    continue

        # 3. Nothing worked
        return []
