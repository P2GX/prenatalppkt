import typing 
from abc import ABC, abstractmethod
from hpotk import MinimalTerm
import hpotk

from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.term_observation import TermObservation

class SonographicMeasurement(ABC):

    _parent: MinimalTerm
    _increased: MinimalTerm
    _decreased: MinimalTerm

    def __init__(self, parent_term: MinimalTerm, increased_term: MinimalTerm, decreased_term: MinimalTerm) -> None: # pyright: ignore[reportAttributeAccessIssue]
        self._parent = parent_term
        self._increased = increased_term
        self._decreased = decreased_term

    
    def evaluate(self, gestational_age: GestationalAge, measurement: typing.Union[int, float]) -> TermObservation: # type: ignore
        pass


    @abstractmethod
    def name(self)-> str:
        raise NotImplementedError("Need to implemented in subclass")

    