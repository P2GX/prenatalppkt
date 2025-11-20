from enum import Enum


class SectionHeader(Enum):
    """
    Enum for the different headers in the ViewPoint6 text export

    Args:
        Enum (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    CLINICAL_IMPRESSION = "Impression"
    CLINICAL_INDICATIONS = "Indication"
    PATIENT_HISTORY = "History"
    MATERNAL_ASSESSMENT = "Maternal Assessment"
    ULTRASOUND_METHOD = "Method"
    PREGNANCY = "Pregnancy"
    PREGNANCY_PROGRESSION = "Dating"
    FETAL_GROWTH_OVERVIEW = "Fetal Growth Overview"
    FETAL_BIOMETRY = "Fetal Biometry"
    GENERAL_EVALUATION = "General Evaluation"
    FETAL_ANATOMY = "Fetal Anatomy"
    FETAL_ECHO = "Fetal Echocardiogram"
    FETAL_DOPPLER = "Fetal Doppler"
    MATERNAL_STRUCTURES = "Maternal Structures"
    FOLLOW_UP_NOTES = "Follow-up"
    CHKD_REFERRAL = "CHKD Referral"

    @classmethod
    def from_string(cls, s: str) -> "SectionHeader":
        """
        Return teh enum member whose value matches the given string

        Args:
            s (str): _description_

        Raises:
            ValueError: _description_

        Returns:
            SectionHeader: _description_
        """
        for member in cls:
            if member.value == s:
                return member
        raise ValueError(f"{s!r} is not a valid {cls.__name__}")
