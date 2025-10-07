"""
test_femur_length_measurement.py

Integration tests for the FemurLengthMeasurement class.
Uses NIHCD reference thresholds for femur length at 20.86 weeks
(Non-Hispanic White population) to verify correct percentile bin
classification and ontology (HPO) term mapping.

Reference: FGCalculatorPercentileRange.pdf (NIHCD dataset)
"""

import pytest
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.femur_length_measurement import FemurLengthMeasurement
from prenatalppkt.measurements.measurement_result import MeasurementResult


@pytest.fixture
def reference_range() -> ReferenceRange:
    """
    NIHCD femur length reference thresholds at 20.86 weeks.
    Percentiles correspond to:
    [3rd, 5th, 10th, 50th, 90th, 95th, 97th]
    """
    thresholds = [29.13, 29.71, 30.64, 34.16, 38.08, 39.27, 40.07]
    ga = GestationalAge.from_weeks(20.86)
    return ReferenceRange(gestational_age=ga, percentiles=thresholds)


@pytest.fixture
def measurement() -> FemurLengthMeasurement:
    """Instantiate the Femur Length measurement class."""
    return FemurLengthMeasurement()


# ---------------------------------------------------------
# Test 1: ReferenceRange categorization
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "value, expected_method, expected_bin",
    [
        (28.0, MeasurementResult.below_3p, "below_3p"),
        (29.3, MeasurementResult.between_3p_5p, "between_3p_5p"),
        (30.0, MeasurementResult.between_5p_10p, "between_5p_10p"),
        (32.0, MeasurementResult.between_10p_50p, "between_10p_50p"),
        (36.0, MeasurementResult.between_50p_90p, "between_50p_90p"),
        (38.6, MeasurementResult.between_90p_95p, "between_90p_95p"),
        (39.5, MeasurementResult.between_95p_97p, "between_95p_97p"),
        (41.0, MeasurementResult.above_97p, "above_97p"),
    ],
)
def test_reference_range_returns_correct_measurement_result(
    reference_range: ReferenceRange, value: float, expected_method, expected_bin: str
):
    """Ensure reference range evaluation yields expected bin and flags."""
    result = reference_range.evaluate(value)
    expected = expected_method()

    # Check percentile bounds
    assert result._lower == expected._lower
    assert result._upper == expected._upper

    # Check canonical bin key and name
    assert result.get_bin_key == expected_bin
    assert result.bin_name == expected_bin

    # Validate logical categorization flags
    if expected_bin == "below_3p":
        assert result.is_below_extreme()
    elif expected_bin == "above_97p":
        assert result.is_above_extreme()
    elif expected_bin in {
        "between_3p_5p",
        "between_5p_10p",
        "between_90p_95p",
        "between_95p_97p",
    }:
        assert result.is_abnormal()
    else:
        assert not result.is_abnormal()


# ---------------------------------------------------------
# Test 2: Femur Length Measurement evaluation -- ontology + observed
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "value, expected_label, expected_observed",
    [
        (28.0, "Short fetal femur length", True),  # HP:0011428
        (29.3, "Short femur", True),  # HP:0003097
        (30.0, "Abnormal femur morphology", True),  # HP:0002823
        (34.5, None, False),  # 10th-90th (normal)
        (37.0, None, False),  # 10th-90th (normal)
        (39.5, None, False),  # 95th-97th (no term)
        (41.0, None, False),  # >=97th (no term)
    ],
)
def test_femur_length_measurement_evaluate(
    measurement: FemurLengthMeasurement,
    reference_range: ReferenceRange,
    value: float,
    expected_label: str,
    expected_observed: bool,
):
    """
    Verify that each percentile bin produces the correct ontology term
    and observed flag in the TermObservation output.
    """
    ga = GestationalAge.from_weeks(20.86)
    observation = measurement.evaluate(
        gestational_age=ga, measurement_value=value, reference_range=reference_range
    )

    if expected_label is None:
        # Normal or unassigned bins: no ontology term assigned
        assert observation.hpo_term is None
    else:
        assert observation.hpo_label == expected_label

    assert observation.observed is expected_observed
