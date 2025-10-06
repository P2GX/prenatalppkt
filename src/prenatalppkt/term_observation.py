from dataclasses import dataclass

from prenatalppkt.scripts.gestational_age import GestationalAge


@dataclass
class TermObservation:
    hpo_id: str
    hpo_label: str
    observed: bool
    gestational_age: GestationalAge
