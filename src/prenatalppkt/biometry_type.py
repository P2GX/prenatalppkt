"""
biometry_type.py

Enumeration of supported biometric measurement types.
Separated into its own module to avoid circular imports.
"""

from enum import Enum


class BiometryType(Enum):
    """Types of biometric measurements supported by this library."""

    HEAD_CIRCUMFERENCE = "head_circumference"
    BIPARIETAL_DIAMETER = "biparietal_diameter"
    ABDOMINAL_CIRCUMFERENCE = "abdominal_circumference"
    FEMUR_LENGTH = "femur_length"
    OCCIPITOFRONTAL_DIAMETER = "occipitofrontal_diameter"
    ESTIMATED_FETAL_WEIGHT = "estimated_fetal_weight"
