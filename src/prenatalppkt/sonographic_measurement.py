import typing
from abc import ABC, abstractmethod
from hpotk import MinimalTerm

from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.term_observation import TermObservation
from prenatalppkt.measurements.measurement_result import MeasurementResult


class SonographicMeasurement(ABC):
    """
    Abstract base class for fetal biometric measurements (e.g., BPD, HC, AC).

    Each subclass defines ontology relationships (HPO terms) and uses
    percentile-based rules to infer whether the observed value represents
    an abnormality (e.g., microcephaly or macrocephaly).

    This class uses `hpotk.MinimalTerm` to ensure ontology consistency.
    """

    _parent_term: MinimalTerm
    _increased_term: MinimalTerm
    _decreased_term: MinimalTerm
    _configurable_bins: typing.Dict[str, typing.Tuple[int, int]]

    def __init__(
        self,
        parent_term: MinimalTerm,
        increased_term: MinimalTerm,
        decreased_term: MinimalTerm,
        bins: typing.Optional[typing.Dict[str, typing.Tuple[int, int]]] = None,
    ) -> None:
        """
        Initialize the ontology and percentile bin configuration.

        Parameters
        ----------
        bins : dict, optional
            Dictionary defining percentile bin ranges for each category, e.g.:
            {
                "extreme_low": (0, 3),
                "abnormal_low": (3, 10),
                "abnormal_high": (90, 97),
                "extreme_high": (97, 100)
            }
        """
        self._parent_term = parent_term
        self._increased_term = increased_term
        self._decreased_term = decreased_term
        self._configurable_bins = bins or {
            "extreme_low": (0, 3),
            "abnormal_low": (3, 10),
            "abnormal_high": (90, 97),
            "extreme_high": (97, 100),
        }

    @property
    def bins(self) -> typing.Dict[str, typing.Tuple[int, int]]:
        """Return the currently configured percentile bins."""
        return self._configurable_bins

    @abstractmethod
    def name(self) -> str:
        """Return the name of this sonographic measurement."""
        raise NotImplementedError("Must be implemented by subclasses.")

    def evaluate(
        self, gestational_age: GestationalAge, result: MeasurementResult
    ) -> TermObservation:
        """
        Evaluate a MeasurementResult and return a phenotype observation
        encoded as a TermObservation.

        Rules (default configuration)
        -----------------------------
        - <=3rd percentile -> decreased_term
        - >=97th percentile -> increased_term
        - (3-10) or (90-97) -> parent_term, observed=True (abnormal)
        - Otherwise -> parent_term, observed=False (normal)
        """

        if result.is_below_extreme():
            term = self._decreased_term
            observed = True
        elif result.is_above_extreme():
            term = self._increased_term
            observed = True
        elif result.is_abnormal():
            term = self._parent_term
            observed = True
        else:
            term = self._parent_term
            observed = False

        return TermObservation(
            hpo_term=term, observed=observed, gestational_age=gestational_age
        )
