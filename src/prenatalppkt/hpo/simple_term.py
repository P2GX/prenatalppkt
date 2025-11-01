



class SimpleTerm:
    _hpo_id: str
    _hpo_label: str


    def __init__(self, hpo_id: str, hpo_label: str) -> None:
        if len(hpo_id) != 10:
            raise ValueError(f"Malformed HPO id:{hpo_id}")
        if len(hpo_label) == 0:
            raise ValueError(f"Malformed HPO label (empty)")
        self._hpo_id = hpo_id
        self._hpo_label = hpo_label

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