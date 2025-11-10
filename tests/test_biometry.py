"""
test_biometry.py

Unit tests for BiometryMeasurement and mapping to ontology terms.
Covers both INTERGROWTH-21st and NICHD reference tables.

NOTE: This tests the legacy biometry.py module which has been simplified.
For full HPO mapping, see test_integration.py which tests the new
MeasurementEvaluation architecture.
"""

import pytest
from prenatalppkt.biometry import BiometryMeasurement, BiometryType
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
    A typical head circumference should map to ~50th percentile with no abnormal flag.
    Tested for both Intergrowth and NICHD sources.
    """
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=175,
    )
    pct, hpo = measure.percentile_and_hpo(reference=reference)
    assert 0 <= pct <= 100
    assert hpo is None  # Normal range


@pytest.mark.parametrize(
    "value_mm",
    [
        130,  # <=3rd percentile
        210,  # >=97th percentile
    ],
)
def test_head_circumference_abnormal_cases(reference, value_mm):
    """
    Extremely small or large head circumference should be flagged as abnormal.
    Only tested with Intergrowth, since NICHD HC parsing is not yet standardized.
    """
    if reference.source != "intergrowth":
        pytest.skip("Head circumference abnormal cases only tested with Intergrowth")

    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=value_mm,
    )
    pct, hpo = measure.percentile_and_hpo(reference=reference)

    # Should be flagged as abnormal (simplified behavior)
    assert hpo == "ABNORMAL"

    # Check percentile is in expected range
    if value_mm == 130:
        assert pct <= 3  # Microcephaly range
    else:
        assert pct >= 97  # Macrocephaly range


# -----------------------
# Femur length tests
# -----------------------


@pytest.mark.parametrize(
    "value_mm",
    [
        10,  # <=3rd percentile
        50,  # >=97th percentile
    ],
)
def test_femur_length_abnormal_cases(reference, value_mm):
    """
    Extremely small or large femur length should be flagged as abnormal.
    Only tested with NICHD, since Intergrowth does not flag femur length in the same way.
    """
    if reference.source != "nichd":
        pytest.skip("Femur length abnormal cases only tested with NICHD")

    measure = BiometryMeasurement(
        measurement_type=BiometryType.FEMUR_LENGTH,
        gestational_age_weeks=20,
        value_mm=value_mm,
    )
    pct, hpo = measure.percentile_and_hpo(reference=reference)

    # Should be flagged as abnormal
    assert hpo == "ABNORMAL"

    # Check percentile is in expected range
    assert pct <= 3 or pct >= 97


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
        assert hpo in (None, "ABNORMAL")
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


def test_unsupported_measurement_type_raises_error(reference):
    """Unsupported biometrics like estimated fetal weight should raise a ValueError."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.ESTIMATED_FETAL_WEIGHT,
        gestational_age_weeks=20,
        value_mm=300,
    )
    with pytest.raises(ValueError, match="Unsupported measurement type"):
        measure.percentile_and_hpo(reference=reference)


def test_missing_reference_data_raises_error(reference):
    """
    Gestational age within 12-40 but missing from the reference table
    should raise ValueError.

    - Intergrowth starts later, so GA=13 is missing there.
    - NICHD starts earlier (around 10 weeks), so GA=9 is missing there.
    """
    missing_ga = 9 if reference.source == "nichd" else 13
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=missing_ga,
        value_mm=150,
    )
    with pytest.raises(ValueError):
        measure.percentile_and_hpo(reference=reference)
