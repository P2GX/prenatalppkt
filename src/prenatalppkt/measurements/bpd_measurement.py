import hpotk
from prenatalppkt.sonographic_measurement import SonographicMeasurement
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.measurement_result import MeasurementResult
from prenatalppkt.term_observation import TermObservation


ABN_SKULL_SIZE = hpotk.MinimalTerm.create_minimal_term(
    term_id="HP:0000240",
    name="Abnormality of skull size",
    alt_term_ids=[],
    is_obsolete=False,
)
INCREASED_SKULL_SIZE = hpotk.MinimalTerm.create_minimal_term(
    term_id="HP:0040194",
    name="Increased head circumference",
    alt_term_ids=[],
    is_obsolete=False,
)
DECREASED_SKULL_SIZE = hpotk.MinimalTerm.create_minimal_term(
    term_id="HP:0040195",
    name="Decreased head circumference",
    alt_term_ids=[],
    is_obsolete=False,
)


class BiparietalDiameterMeasurement(SonographicMeasurement):
    """
    Implements BPD (biparietal diameter) measurement evaluation logic.

    This class maps percentile-based measurement results to
    the appropriate Human Phenotype Ontology (HPO) term and
    whether an abnormal finding is observed.

    - ≤3rd percentile  → Decreased head circumference
    - ≥97th percentile → Increased head circumference
    - 3rd–10th or 90th–97th percentile → Abnormality of skull size (mild)
    - 10th–90th percentile → Abnormality of skull size (normal range, not observed)
    """

    def __init__(self) -> None:
        super().__init__(
            parent_term=ABN_SKULL_SIZE,
            increased_term=INCREASED_SKULL_SIZE,
            decreased_term=DECREASED_SKULL_SIZE,
        )

    def evaluate(
        self, gestational_age: GestationalAge, measurement_result: MeasurementResult
    ) -> TermObservation:
        """
        Map a percentile-based measurement result to an HPO term.

        Parameters
        ----------
        gestational_age : GestationalAge
            Gestational age at the time of the measurement.
        measurement_result : MeasurementResult
            The percentile bin outcome for the measured biometric.

        Returns
        -------
        TermObservation
            Observation linking HPO term and whether abnormality is observed.
        """
        # Extreme small or large
        if measurement_result.is_below_extreme():
            return TermObservation(
                hpo_term=self._decreased_term,
                observed=True,
                gestational_age=gestational_age,
            )

        if measurement_result.is_above_extreme():
            return TermObservation(
                hpo_term=self._increased_term,
                observed=True,
                gestational_age=gestational_age,
            )

        # Mildly abnormal (3–10 or 90–97)
        if measurement_result.is_abnormal():
            return TermObservation(
                hpo_term=self._parent_term,
                observed=True,
                gestational_age=gestational_age,
            )

        # Normal range → parent term, but observed=False
        return TermObservation(
            hpo_term=self._parent_term, observed=False, gestational_age=gestational_age
        )

    def name(self) -> str:
        """Return the canonical name for this measurement."""
        return "biparietal diameter"
