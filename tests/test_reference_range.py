"""
test_reference_range.py

Tests for the ReferenceRange and MeasurementResult classes.

All tests are derived from the NIHCD fetal growth reference data for
biparietal diameter (BPD) at gestational week 20.86, Non-Hispanic White.
Threshold values are taken from the NIHCD table (see FGCalculatorPercentileRange.pdf).

This test ensures that percentile bins are correctly returned across
all defined measurement ranges (<=3rd, 3rd-5th, 5th-10th, 10th-50th, 50th-90th,
90th-95th, 95th-97th, >=97th).
"""

import pytest
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.measurement_result import MeasurementResult


@pytest.fixture
def reference_range() -> ReferenceRange:
    """
    Fixture representing the NIHCD percentile cutoffs for BPD at 20.86 weeks.
    Thresholds correspond to:
        3rd, 5th, 10th, 50th, 90th, 95th, 97th percentiles.
    """
    thresholds = [145.25, 147.25, 150.37, 161.95, 174.41, 178.12, 180.56]
    ga = GestationalAge.from_weeks(20.86)
    return ReferenceRange(gestational_age=ga, percentiles=thresholds)


@pytest.mark.parametrize(
    "value, expected_method",
    [
        (140.0, MeasurementResult.below_3p),
        (146.0, MeasurementResult.between_3p_5p),
        (149.0, MeasurementResult.between_5p_10p),
        (155.0, MeasurementResult.between_10p_50p),
        (170.0, MeasurementResult.between_50p_90p),
        (176.0, MeasurementResult.between_90p_95p),
        (179.0, MeasurementResult.between_95p_97p),
        (185.0, MeasurementResult.above_97p),
    ],
)
def test_reference_range_bin_mapping(
    reference_range: ReferenceRange, value: float, expected_method
):
    """
    Verify that ReferenceRange.evaluate() assigns the correct MeasurementResult
    static method for each percentile bin based on value.
    """
    result = reference_range.evaluate(value)
    expected = expected_method()
    assert result._lower == expected._lower
    assert result._upper == expected._upper
