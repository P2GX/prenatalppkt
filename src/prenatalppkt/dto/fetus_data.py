import typing
from ..hpo.simple_term import SimpleTerm
from .measurements_data import MeasurementsData


class FetusData:
    """
    Data transfer object for fetal phenotype and attributes
    """

    # _mother_id: str
    # _maternal_age_at_exam: str
    _hpo_term_list: typing.List[SimpleTerm]

    def __init__(
        self,
        hpo_term_list: typing.List[SimpleTerm],
        measurements: typing.Optional[MeasurementsData] = None,
        fetus_number: typing.Optional[int] = None,
        gender: typing.Optional[str] = None,
        ga_by_sonography: typing.Optional[float] = None,
        heart_bpm: typing.Optional[int] = None,
        heart_rate_is: typing.Optional[str] = None,
        fetus_growth: typing.Optional[str] = None,
        fetus_presentation: typing.Optional[str] = None,
    ) -> None:
        """Encapsulates phenotype and biometric data for one fetus."""
        self._hpo_term_list = hpo_term_list ## todo, add the Gestational Age from the exam to each SimpleTerm
        self.measurements = measurements
        self.fetus_number = fetus_number
        self.gender = gender
        self.ga_by_sonography = ga_by_sonography
        self.heart_bpm = heart_bpm
        self.heart_rate_is = heart_rate_is
        self.fetus_growth = fetus_growth
        self.fetus_presentation = fetus_presentation

    @property
    def hpo_term_list(self):
        """
        Return list of HPO terms linked to fetal phenotype
        """
        return self._hpo_term_list

    def __repr__(self):
        return (
            f"FetusData(fetus_number={self.fetus_number}, "
            f"gender={self.gender}, GA={self.ga_by_sonography}, "
            f"measurements={self.measurements})"
        )
