


class TermBin:
    def __init__(self, termid: str, termlabel: str, normal: bool) -> None:
        self._termid = termid
        self._termlabel = termlabel
        self._normal = normal

    @property
    def termid(self) -> str:
        """Return the HPO term ID (e.g., 'HP:0000252')."""
        return self._termid

    @property
    def termlabel(self) -> str:
        """Return the human-readable label of the term."""
        return self._termlabel

    @property
    def normal(self) -> bool:
        """Return True if the term represents a normal finding."""
        return self._normal