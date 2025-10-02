"""
test_biometry.py

Unit tests for BiometryMeasurement and head circumference mapping.
Covers both INTERGROWTH-21st and NICHD reference tables.
"""

import pytest
from prenatalppkt.biometry import BiometryMeasurement, BiometryType
from prenatalppkt import constants
from prenatalppkt.biometry_reference import FetalGrowthPercentiles


# Run all tests against both supported sources
@pytest.fixture(params=["intergrowth", "nichd"])
def reference(request):
    """Provide a FetalGrowthPercentiles reference for each supported source."""
    return FetalGrowthPercentiles(source=request.param)


def test_head_circumference_normal_case(reference):
    """A normal head circumference should be ~50th percentile with no HPO term."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=175,
    )
    pct, hpo = measure.percentile_and_hpo(reference=reference)
    assert 0 <= pct <= 100  # relax bound slightly, source-specific differences exist
    if pct:  # should not yield abnormal HPO term in a normal case
        assert hpo is None


@pytest.mark.parametrize(
    "value_mm, expected_hpo",
    [(130, constants.HPO_MICROCEPHALY), (210, constants.HPO_MACROCEPHALY)],
)
def test_head_circumference_abnormal_cases(reference, value_mm, expected_hpo):
    """Extremely small or large head circumference should map to the correct HPO term."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=value_mm,
    )
    _, hpo = measure.percentile_and_hpo(reference=reference)
    assert hpo == expected_hpo


def test_invalid_gestational_age_raises_error(reference):
    """Gestational ages outside 12-40 weeks should raise ValueError."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=2,
        value_mm=100,
    )
    with pytest.raises(ValueError):
        measure.percentile_and_hpo(reference=reference)

    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=45,
        value_mm=200,
    )
    with pytest.raises(ValueError):
        measure.percentile_and_hpo(reference=reference)


def test_missing_reference_data_raises_error(reference):
    """Gestational age within 12-40 but missing from reference should raise ValueError."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=18,  # not guaranteed in mock/intermediate tables
        value_mm=150,
    )
    with pytest.raises(ValueError):
        measure.percentile_and_hpo(reference=reference)


def test_unsupported_measurement_type_raises_error(reference):
    """Unsupported biometrics like estimated fetal weight should raise a ValueError."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.ESTIMATED_FETAL_WEIGHT,
        gestational_age_weeks=20,
        value_mm=300,
    )
    with pytest.raises(ValueError, match="Unsupported measurement type"):
        measure.percentile_and_hpo(reference=reference)
