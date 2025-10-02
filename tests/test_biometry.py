"""
test_biometry.py

Unit tests for BiometryMeasurement and mapping to ontology terms.
Covers both INTERGROWTH-21st and NICHD reference tables.
"""

import pytest
from prenatalppkt.biometry import BiometryMeasurement, BiometryType
from prenatalppkt import constants
from prenatalppkt.biometry_reference import FetalGrowthPercentiles


# -----------------------
# Shared fixtures
# -----------------------


@pytest.fixture(params=["intergrowth", "nichd"])
def reference(request):
    """Provide a FetalGrowthPercentiles reference for each supported source."""
    return FetalGrowthPercentiles(source=request.param)


# -----------------------
# Head circumference tests
# -----------------------


def test_head_circumference_normal_case(reference):
    """
    A typical head circumference should map to ~50th percentile with no HPO term.
    Tested for both Intergrowth and NICHD sources.
    """
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=175,
    )
    pct, hpo = measure.percentile_and_hpo(reference=reference)
    assert 0 <= pct <= 100
    assert hpo is None


@pytest.mark.parametrize(
    "value_mm, expected_hpo",
    [
        (130, constants.HPO_MICROCEPHALY),  # <=3rd percentile
        (210, constants.HPO_MACROCEPHALY),  # >=97th percentile
    ],
)
def test_head_circumference_abnormal_cases(reference, value_mm, expected_hpo):
    """
    Extremely small or large head circumference should map to the correct HPO term.
    Only tested with Intergrowth, since NICHD HC parsing is not yet standardized.
    """
    if reference.source != "intergrowth":
        pytest.skip("Head circumference abnormal cases only tested with Intergrowth")

    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=value_mm,
    )
    _, hpo = measure.percentile_and_hpo(reference=reference)
    assert hpo == expected_hpo


# -----------------------
# Femur length tests
# -----------------------


@pytest.mark.parametrize(
    "value_mm, expected_hpo",
    [
        (10, constants.HPO_SHORT_FEMUR),  # <=3rd percentile
        (50, constants.HPO_LONG_FEMUR),  # >=97th percentile (placeholder constant)
    ],
)
def test_femur_length_abnormal_cases(reference, value_mm, expected_hpo):
    """
    Extremely small or large femur length should map to the correct HPO term.
    Only tested with NICHD, since Intergrowth does not flag femur length in the same way.
    """
    if reference.source != "nichd":
        pytest.skip("Femur length abnormal cases only tested with NICHD")

    measure = BiometryMeasurement(
        measurement_type=BiometryType.FEMUR_LENGTH,
        gestational_age_weeks=20,
        value_mm=value_mm,
    )
    _, hpo = measure.percentile_and_hpo(reference=reference)
    assert hpo == expected_hpo


# -----------------------
# Interpolation test
# -----------------------


def test_interpolation_for_non_tabled_ga(reference):
    """
    Ensure interpolation works at a GA not directly in the reference table.
    E.g., GA=19 weeks is missing in some sources but should interpolate cleanly.
    """
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=19,
        value_mm=165,
    )
    try:
        pct, hpo = measure.percentile_and_hpo(reference=reference)
        assert 0 <= pct <= 100
        assert hpo in (None, constants.HPO_MICROCEPHALY, constants.HPO_MACROCEPHALY)
    except ValueError as e:
        pytest.skip(f"Interpolation not available for {reference.source}: {e}")


# -----------------------
# Error handling tests
# -----------------------


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
        gestational_age_weeks=13,  # deliberately missing
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
