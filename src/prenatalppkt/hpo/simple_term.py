import typing
from prenatalppkt.gestational_age import GestationalAge


class SimpleTerm:
    """
    Simple representation of an HPO term with ID and label
    """

    _hpo_id: str
    _hpo_label: str

    def __init__(
        self,
        hpo_id: str,
        hpo_label: str,
        excluded=False,
        observed: typing.Optional[GestationalAge] = None,
    ) -> None:
        if len(hpo_id) != 10:
            raise ValueError(f"Malformed HPO id:{hpo_id}")
        if len(hpo_label) == 0:
            raise ValueError("Malformed HPO label (empty)")
        self._hpo_id = hpo_id
        self._hpo_label = hpo_label
        self._excluded = excluded
        self._observed = observed

    @property
    def hpo_id(self) -> str:
        """
        :returns: The HPO identifier, e.g., HP:0001166
        :rtype: str
        """
        return self._hpo_id

    @property
    def hpo_label(self) -> str:
        """
        :returns: The HPO label, e.g., Arachnodactyly
        :rtype: str
        """
        return self._hpo_label

    @property
    def excluded(self) -> bool:
        """
        :returns: the HPO status, e.g., excluded/included (T/F or 0/1)
        :rtype: bool
        """
        return self._excluded

    @property
    def observed(self) -> typing.Optional[GestationalAge]:
        """
        :returns: the gestational age when a phenotypic feature was observed
        :rtype: Optional
        """
        return self._observed

    def __repr__(self) -> str:
        if self._excluded:
            return f"{self._hpo_label}({self._hpo_id})(excluded)"
        else:
            return f"{self._hpo_label}({self._hpo_id})"
