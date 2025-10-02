"""
test_biometry.py

Unit tests for BiometryMeasurement and head circumference mapping.
"""

import pytest
from prenatalppkt.biometry import BiometryMeasurement, BiometryType
from prenatalppkt import constants
from prenatalppkt.biometry_reference import FetalGrowthPercentiles


# Initialize a global reference object for consistency across tests
REFERENCE = FetalGrowthPercentiles(source="intergrowth")


def test_head_circumference_normal_case():
    """A normal head circumference should be ~50th percentile with no HPO term."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=175,
    )
    pct, hpo = measure.percentile_and_hpo(reference=REFERENCE)
    assert 40 <= pct <= 60
    assert hpo is None


@pytest.mark.parametrize(
    "value_mm, expected_hpo",
    [(130, constants.HPO_MICROCEPHALY), (210, constants.HPO_MACROCEPHALY)],
)
def test_head_circumference_abnormal_cases(value_mm, expected_hpo):
    """Extremely small or large head circumference should map to the correct HPO term."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=value_mm,
    )
    _, hpo = measure.percentile_and_hpo(reference=REFERENCE)
    assert hpo == expected_hpo


def test_invalid_gestational_age_raises_error():
    """Gestational ages outside 12-40 weeks should raise ValueError."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=2,
        value_mm=100,
    )
    with pytest.raises(ValueError):
        measure.percentile_and_hpo(reference=REFERENCE)

    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=45,
        value_mm=200,
    )
    with pytest.raises(ValueError):
        measure.percentile_and_hpo(reference=REFERENCE)


def test_missing_reference_data_raises_error():
    """Gestational age within 12-40 but missing from reference should raise ValueError."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=18,  # not in mock reference
        value_mm=150,
    )
    with pytest.raises(ValueError):
        measure.percentile_and_hpo(reference=REFERENCE)
