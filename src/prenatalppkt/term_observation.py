from dataclasses import dataclass
from hpotk import MinimalTerm
from prenatalppkt.gestational_age import GestationalAge


@dataclass
class TermObservation:
    """
    Represents the observed result of a sonographic measurement relative to
    an ontology term and percentile-based interpretation.

    Attributes
    ----------
    hpo_term : MinimalTerm
        The ontology term representing the abnormality or normal finding.
    hpo_id : str
        The HPO identifier string (e.g., "HP:0000240").
    hpo_label : str
        The human-readable name of the HPO term (e.g., "Abnormality of skull size").
    observed : bool
        Whether the phenotype was observed (True) or excluded (False).
    gestational_age : GestationalAge
        The gestational age context for the observation.
    """

    hpo_term: MinimalTerm
    observed: bool
    gestational_age: GestationalAge
    hpo_id: str = ""
    hpo_label: str = ""

    def __post_init__(self) -> None:
        """
        Populate the HPO ID and label automatically from the MinimalTerm
        if not explicitly provided.
        """
        if isinstance(self.hpo_term, MinimalTerm):
            if not self.hpo_id:
                self.hpo_id = getattr(self.hpo_term, "term_id", "")
            if not self.hpo_label:
                self.hpo_label = getattr(self.hpo_term, "name", "")

    def __repr__(self) -> str:
        """
        Developer-friendly representation showing label and observation state.
        """
        return (
            f"TermObservation(hpo_label='{self.hpo_label}', "
            f"observed={self.observed}, "
            f"gestational_age={self.gestational_age.weeks}w{self.gestational_age.days}d)"
        )
