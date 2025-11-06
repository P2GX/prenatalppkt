class ExamData:
    """
    Data transfer object for maternal exam metadata
    """

    _mother_id: str
    _maternal_age_at_exam: str

    def __init__(self, mother_id, maternal_age_at_exam) -> None:
        self._mother_id = mother_id
        self._maternal_age_at_exam = maternal_age_at_exam

    @property
    def mother_id(self):
        """
        Return unique identifier for the mother
        """
        return self._mother_id

    @property
    def maternal_age_at_exam(self):
        """
        Return maternal age recorded at time of exam
        """
        return self._maternal_age_at_exam
