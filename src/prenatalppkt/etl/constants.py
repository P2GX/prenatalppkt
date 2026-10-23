"""
Constants and enums for ETL pipeline.

Provides standardized names and mappings across different input formats.
"""

from enum import Enum
from typing import Dict, Set

from prenatalppkt.etl.measurement_registry import REGISTRY


class BiometryMeasurement(Enum):
    """
    Standardized biometry measurement names across all input formats.

    Values represent the standard name used throughout the ETL pipeline.
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
    TIBIA_LENGTH = "Tibia"
    FIBULA_LENGTH = "Fibula"
    RADIUS_LENGTH = "Radius"
    ULNA_LENGTH = "Ulna"
    FOOT_LENGTH = "Foot"
    CISTERNA_MAGNA = "Cisterna Magna"
    NASAL_BONE = "Nasal Bone"
    LATERAL_VENTRICLE_LEFT = "Lateral Vent left"
    LATERAL_VENTRICLE_RIGHT = "Lateral Vent right"
    BIORBITAL_DIAMETER = "Biorbit"
    MEAN_GESTATIONAL_SAC = "Mean Gest Sac"

    @classmethod
    def from_string(cls, s: str) -> "BiometryMeasurement":
        """
        Return the enum member whose standard name matches the given string.

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
        """Return set of all standard measurement names."""
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


# Mapping of input-specific names to standardized BiometryMeasurement, one map
# per input format, plus GENERIC_NAME_MAP for common spelling variants. All
# four are built from the measurement registry, which is where names are added.


def _name_map(source: str) -> Dict[str, BiometryMeasurement]:
    return {
        label: BiometryMeasurement(spec.name)
        for spec in REGISTRY.values()
        for label in spec.all_aliases(source)
    }


OBSERVER_NAME_MAP: Dict[str, BiometryMeasurement] = _name_map("observer")
VIEWPOINT_TEXT_NAME_MAP: Dict[str, BiometryMeasurement] = _name_map("viewpoint_text")
VIEWPOINT_HL7_NAME_MAP: Dict[str, BiometryMeasurement] = _name_map("viewpoint_hl7")
GENERIC_NAME_MAP: Dict[str, BiometryMeasurement] = _name_map("generic")


def normalize_measurement_name(
    raw_name: str, format_map: Dict[str, BiometryMeasurement] = None
) -> str:
    """
    Normalize a raw measurement name to standard form.

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
