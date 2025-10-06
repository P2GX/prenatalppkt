import typing
import hpotk
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.scripts.sonographic_measurement import SonographicMeasurement
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


class BiparietalDiameterMeasuremnt(SonographicMeasurement):
    def __init__(self) -> None:
        super().__init__(
            parent_term=ABN_SKULL_SIZE,
            increased_term=INCREASED_SKULL_SIZE,
            decreased_term=DECREASED_SKULL_SIZE,
        )

    def name(self) -> str:
        return "biparietal diameter"
