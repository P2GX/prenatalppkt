"""
test_bpd_measurement.py

Integration tests for the BiparietalDiameterMeasurement class.
Uses NIHCD reference thresholds for BPD at 20.86 weeks (Non-Hispanic White)
to confirm correct HPO term mapping and observed flag behavior.

Reference: FGCalculatorPercentileRange.pdf (NIHCD dataset)
"""

import pytest
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.bpd_measurement import BiparietalDiameterMeasurement
from prenatalppkt.measurements.measurement_result import MeasurementResult


@pytest.fixture
def reference_range() -> ReferenceRange:
    """
    NIHCD BPD reference thresholds at 20.86 weeks.
    """
    thresholds = [145.25, 147.25, 150.37, 161.95, 174.41, 178.12, 180.56]
    ga = GestationalAge.from_weeks(20.86)
    return ReferenceRange(gestational_age=ga, percentiles=thresholds)


@pytest.fixture
def measurement() -> BiparietalDiameterMeasurement:
    """Instantiate the BPD measurement class."""
    return BiparietalDiameterMeasurement()


# ---------------------------------------------------------
# Test 1: ReferenceRange categorization
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "value, expected_method, expected_bin",
    [
        (140.0, MeasurementResult.below_3p, "below_3p"),
        (146.0, MeasurementResult.between_3p_5p, "between_3p_5p"),
        (149.0, MeasurementResult.between_5p_10p, "between_5p_10p"),
        (
            155.0,
            MeasurementResult.between_10p_50p,
            "between_10p_50p",
        ),  # no ontology term for "normal" percentiles
        (
            170.0,
            MeasurementResult.between_50p_90p,
            "between_50p_90p",
        ),  # no ontology term for "normal" percentiles
        (176.0, MeasurementResult.between_90p_95p, "between_90p_95p"),
        (179.0, MeasurementResult.between_95p_97p, "between_95p_97p"),
        (185.0, MeasurementResult.above_97p, "above_97p"),
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
# Test 2: BPD Measurement evaluation -- ontology + observed
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "value, expected_label, expected_observed",
    [
        (140.0, "Microcephaly", True),  # HP:0000252
        (149.0, "Abnormality of skull size", True),  # HP:0000240
        (155.0, None, False),  # normal range
        (170.0, None, False),  # normal range
        (185.0, "Macrocephaly", True),  # HP:0000256
    ],
)
def test_bpd_measurement_evaluate(
    measurement: BiparietalDiameterMeasurement,
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
        # Normal bins: no ontology term assigned
        assert observation.hpo_term is None
    else:
        assert observation.hpo_label == expected_label

    assert observation.observed is expected_observed
