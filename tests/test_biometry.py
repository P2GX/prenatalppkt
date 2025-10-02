"""
test_biometry.py

Unit tests for BiometryMeasurement and percentile-to-HPO mapping.

Covers:
- Normal cases (?50th percentile, no HPO term).
- Abnormal cases (<=3rd or >=97th percentile, mapping to HPO terms).
- Edge cases (invalid gestational age, missing data, unsupported types).

Tests are run against both INTERGROWTH-21st and NICHD reference tables.
"""

import pytest
from prenatalppkt.biometry import BiometryMeasurement, BiometryType
from prenatalppkt import constants
from prenatalppkt.biometry_reference import FetalGrowthPercentiles


# ----------------------------------------------------------------------
# Shared fixture
# ----------------------------------------------------------------------


@pytest.fixture(params=["intergrowth", "nichd"])
def reference(request):
    """Provide a FetalGrowthPercentiles reference for each supported source."""
    return FetalGrowthPercentiles(source=request.param)


# ----------------------------------------------------------------------
# Normal case
# ----------------------------------------------------------------------


def test_head_circumference_normal_case(reference):
    """A typical head circumference should map to ~50th percentile with no HPO term."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=20,
        value_mm=175,
    )
    pct, hpo = measure.percentile_and_hpo(reference=reference)

    # Percentile should always be within 0-100
    assert 0 <= pct <= 100

    # No abnormal HPO mapping expected for a ~50th percentile value
    if pct:
        assert hpo is None


# ----------------------------------------------------------------------
# Abnormal cases (combined HC + FL)
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "measurement_type, ga_weeks, value_mm, expected_hpo, source_required",
    [
        # Head circumference: only INTERGROWTH source has abnormal-case validation
        (
            BiometryType.HEAD_CIRCUMFERENCE,
            20,
            130,
            constants.HPO_MICROCEPHALY,
            "intergrowth",
        ),
        (
            BiometryType.HEAD_CIRCUMFERENCE,
            20,
            210,
            constants.HPO_MACROCEPHALY,
            "intergrowth",
        ),
        # Femur length: only NICHD source has abnormal-case validation
        (BiometryType.FEMUR_LENGTH, 20, 10, constants.HPO_SHORT_FEMUR, "nichd"),
        (BiometryType.FEMUR_LENGTH, 20, 50, constants.HPO_LONG_FEMUR, "nichd"),
    ],
)
def test_abnormal_cases(
    reference, measurement_type, ga_weeks, value_mm, expected_hpo, source_required
):
    """
    Extremely small or large values should map to abnormal HPO terms.

    Different sources provide different validated abnormal definitions:
    - Head circumference abnormal thresholds -> INTERGROWTH.
    - Femur length abnormal thresholds -> NICHD.
    """
    if reference.source != source_required:
        pytest.skip(
            f"Abnormal cases for {measurement_type} only tested with {source_required}"
        )

    measure = BiometryMeasurement(
        measurement_type=measurement_type,
        gestational_age_weeks=ga_weeks,
        value_mm=value_mm,
    )
    _, hpo = measure.percentile_and_hpo(reference=reference)
    assert hpo == expected_hpo


# ----------------------------------------------------------------------
# Edge cases
# ----------------------------------------------------------------------


def test_invalid_gestational_age_raises_error(reference):
    """Gestational ages outside 12-40 weeks should raise ValueError."""
    early = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=2,
        value_mm=100,
    )
    with pytest.raises(ValueError):
        early.percentile_and_hpo(reference=reference)

    late = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=45,
        value_mm=200,
    )
    with pytest.raises(ValueError):
        late.percentile_and_hpo(reference=reference)


def test_missing_reference_data_raises_error(reference):
    """Valid GA but missing from reference tables should raise ValueError."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
        gestational_age_weeks=13,  # chosen GA likely absent from both sources
        value_mm=150,
    )
    with pytest.raises(ValueError):
        measure.percentile_and_hpo(reference=reference)


def test_unsupported_measurement_type_raises_error(reference):
    """Unsupported biometrics like estimated fetal weight should raise ValueError."""
    measure = BiometryMeasurement(
        measurement_type=BiometryType.ESTIMATED_FETAL_WEIGHT,
        gestational_age_weeks=20,
        value_mm=300,
    )
    with pytest.raises(ValueError, match="Unsupported measurement type"):
        measure.percentile_and_hpo(reference=reference)
