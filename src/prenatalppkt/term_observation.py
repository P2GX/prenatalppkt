from dataclasses import dataclass
from hpotk import MinimalTerm
from prenatalppkt.gestational_age import GestationalAge


@dataclass
class TermObservation:
    """
    Encapsulates the outcome of an evaluated measurement linked to an ontology term.

    Attributes
    ----------
    hpo_term : MinimalTerm
        The ontology term representing the phenotype outcome.
    observed : bool
        Whether this phenotype was observed (True) or excluded (False).
    gestational_age : GestationalAge
        The gestational age context in which the measurement was taken.
    """

    hpo_term: MinimalTerm
    observed: bool
    gestational_age: GestationalAge
