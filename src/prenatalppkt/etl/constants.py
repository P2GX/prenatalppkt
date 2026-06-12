"""
Constants and enums for ETL pipeline.

Provides standardized names and mappings across different input formats.
"""

from enum import Enum
from typing import Dict, Set


class BiometryMeasurement(Enum):
    """
    Standardized biometry measurement names across all input formats.

    Values represent the canonical name used throughout the ETL pipeline.
    """

    HEAD_CIRCUMFERENCE = "HC"
    BIPARIETAL_DIAMETER = "BPD"
    ABDOMINAL_CIRCUMFERENCE = "AC"
    FEMUR_LENGTH = "Femur"
    NUCHAL_FOLD = "Nuchal Fold"
    CEREBELLUM = "Cerebellum"
    OCCIPITOFRONTAL_DIAMETER = "OFD"
    HUMERUS_LENGTH = "Humerus"
    CROWN_RUMP_LENGTH = "CRL"
    NUCHAL_TRANSLUCENCY = "NT"

    @classmethod
    def from_string(cls, s: str) -> "BiometryMeasurement":
        """
        Return the enum member whose canonical name matches the given string.

        Args:
            s: String representation of measurement name

        Returns:
            BiometryMeasurement enum member

        Raises:
            ValueError: If string doesn't match any known measurement
        """
        s_clean = s.strip()
        for member in cls:
            if member.value == s_clean:
                return member
        raise ValueError(f"{s!r} is not a valid {cls.__name__}")

    @classmethod
    def all_values(cls) -> Set[str]:
        """Return set of all canonical measurement names."""
        return {member.value for member in cls}


class SectionHeader(Enum):
    """
    Enum for section headers in ViewPoint text exports.

    Extended from viewpoint_text_sections.py to include additional sections.
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
        Return the enum member whose value matches the given string.

        Args:
            s: String representation of section header

        Returns:
            SectionHeader enum member

        Raises:
            ValueError: If string doesn't match any known section
        """
        for member in cls:
            if member.value == s:
                return member
        raise ValueError(f"{s!r} is not a valid {cls.__name__}")


# Mapping of input-specific names to standardized BiometryMeasurement
# This allows each extractor to map its format-specific names to canonical names

OBSERVER_NAME_MAP: Dict[str, BiometryMeasurement] = {
    # Observer JSON uses these exact labels in measurements array
    "HC": BiometryMeasurement.HEAD_CIRCUMFERENCE,
    "BPD": BiometryMeasurement.BIPARIETAL_DIAMETER,
    "AC": BiometryMeasurement.ABDOMINAL_CIRCUMFERENCE,
    "Femur": BiometryMeasurement.FEMUR_LENGTH,
    "Nuchal Fold": BiometryMeasurement.NUCHAL_FOLD,
    "Cerebellum": BiometryMeasurement.CEREBELLUM,
    "OFD": BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER,
    "Humerus": BiometryMeasurement.HUMERUS_LENGTH,
    "CRL": BiometryMeasurement.CROWN_RUMP_LENGTH,
    "NT": BiometryMeasurement.NUCHAL_TRANSLUCENCY,
}

VIEWPOINT_TEXT_NAME_MAP: Dict[str, BiometryMeasurement] = {
    # ViewPoint text uses these labels in Fetal Biometry section
    "HC": BiometryMeasurement.HEAD_CIRCUMFERENCE,
    "BPD": BiometryMeasurement.BIPARIETAL_DIAMETER,
    "AC": BiometryMeasurement.ABDOMINAL_CIRCUMFERENCE,
    "Femur": BiometryMeasurement.FEMUR_LENGTH,
    "Nuchal Fold": BiometryMeasurement.NUCHAL_FOLD,
    "Cerebellum": BiometryMeasurement.CEREBELLUM,
    "OFD": BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER,
    "Humerus": BiometryMeasurement.HUMERUS_LENGTH,
}

VIEWPOINT_HL7_NAME_MAP: Dict[str, BiometryMeasurement] = {
    # ViewPoint HL7 uses LOINC-style names in OBX segments
    "HeadCircumference": BiometryMeasurement.HEAD_CIRCUMFERENCE,
    "BiParietalDiameter": BiometryMeasurement.BIPARIETAL_DIAMETER,
    "AbdominalCircumference": BiometryMeasurement.ABDOMINAL_CIRCUMFERENCE,
    "FemurUndefinedLength": BiometryMeasurement.FEMUR_LENGTH,
    "FemurLength": BiometryMeasurement.FEMUR_LENGTH,
    "NuchalFold": BiometryMeasurement.NUCHAL_FOLD,
    "Cerebellum": BiometryMeasurement.CEREBELLUM,
    "OccipitofrontalDiameter": BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER,
    "HumerusLength": BiometryMeasurement.HUMERUS_LENGTH,
}

# Generic name normalization - catches common variations
GENERIC_NAME_MAP: Dict[str, BiometryMeasurement] = {
    # Head Circumference variations
    "hc": BiometryMeasurement.HEAD_CIRCUMFERENCE,
    "head_circumference": BiometryMeasurement.HEAD_CIRCUMFERENCE,
    "head circumference": BiometryMeasurement.HEAD_CIRCUMFERENCE,
    "headcircumference": BiometryMeasurement.HEAD_CIRCUMFERENCE,
    # Biparietal Diameter variations
    "bpd": BiometryMeasurement.BIPARIETAL_DIAMETER,
    "biparietal_diameter": BiometryMeasurement.BIPARIETAL_DIAMETER,
    "biparietal diameter": BiometryMeasurement.BIPARIETAL_DIAMETER,
    "biparietaldiameter": BiometryMeasurement.BIPARIETAL_DIAMETER,
    # Abdominal Circumference variations
    "ac": BiometryMeasurement.ABDOMINAL_CIRCUMFERENCE,
    "abdominal_circumference": BiometryMeasurement.ABDOMINAL_CIRCUMFERENCE,
    "abdominal circumference": BiometryMeasurement.ABDOMINAL_CIRCUMFERENCE,
    "abdominalcircumference": BiometryMeasurement.ABDOMINAL_CIRCUMFERENCE,
    # Femur Length variations
    "femur": BiometryMeasurement.FEMUR_LENGTH,
    "fl": BiometryMeasurement.FEMUR_LENGTH,
    "femur_length": BiometryMeasurement.FEMUR_LENGTH,
    "femur length": BiometryMeasurement.FEMUR_LENGTH,
    "femurlength": BiometryMeasurement.FEMUR_LENGTH,
    "femurundefinedlength": BiometryMeasurement.FEMUR_LENGTH,
    # Nuchal Fold variations (including single-word "nuchal" from ViewPoint text)
    "nuchal": BiometryMeasurement.NUCHAL_FOLD,
    "nuchal_fold": BiometryMeasurement.NUCHAL_FOLD,
    "nuchal fold": BiometryMeasurement.NUCHAL_FOLD,
    "nuchalfold": BiometryMeasurement.NUCHAL_FOLD,
    # Cerebellum variations
    "cerebellum": BiometryMeasurement.CEREBELLUM,
    # Occipitofrontal Diameter variations
    "ofd": BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER,
    "occipitofrontal_diameter": BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER,
    "occipitofrontal diameter": BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER,
    "occipito-frontal diameter": BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER,
    "occipitofrontaldiameter": BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER,
    # Humerus Length variations
    "humerus": BiometryMeasurement.HUMERUS_LENGTH,
    "hl": BiometryMeasurement.HUMERUS_LENGTH,
    "humerus_length": BiometryMeasurement.HUMERUS_LENGTH,
    "humerus length": BiometryMeasurement.HUMERUS_LENGTH,
    "humeruslength": BiometryMeasurement.HUMERUS_LENGTH,
}


def normalize_measurement_name(
    raw_name: str, format_map: Dict[str, BiometryMeasurement] = None
) -> str:
    """
    Normalize a raw measurement name to canonical form.

    First tries format-specific mapping (if provided), then falls back to generic mapping.

    Args:
        raw_name: Raw measurement name from input file
        format_map: Format-specific name mapping (optional)

    Returns:
        Canonical measurement name (from BiometryMeasurement enum)

    Raises:
        ValueError: If name cannot be normalized

    Example:
        TODO @VarenyaJ
    """
    # Try format-specific mapping first
    if format_map and raw_name in format_map:
        return format_map[raw_name].value

    # Try exact match with generic mapping
    if raw_name in GENERIC_NAME_MAP:
        return GENERIC_NAME_MAP[raw_name].value

    # Try case-insensitive match with generic mapping
    raw_name_lower = raw_name.lower().strip()
    if raw_name_lower in GENERIC_NAME_MAP:
        return GENERIC_NAME_MAP[raw_name_lower].value

    # No match found
    raise ValueError(f"Cannot normalize measurement name: {raw_name}")


def is_target_measurement(
    raw_name: str, format_map: Dict[str, BiometryMeasurement] = None
) -> bool:
    """
    Check if a raw measurement name corresponds to a target biometry.

    Args:
        raw_name: Raw measurement name from input file
        format_map: Format-specific name mapping (optional)

    Returns:
        True if this is a target measurement, False otherwise

    Example:
        >>> is_target_measurement("HC")
        True
        >>> is_target_measurement("unknown_measurement")
        False
    """
    try:
        normalize_measurement_name(raw_name, format_map)
        return True
    except ValueError:
        return False
