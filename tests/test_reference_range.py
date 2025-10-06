import pytest
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.measurement_result import MeasurementResult


@pytest.fixture
def ref_range() -> ReferenceRange:
    """
    Create MeasurementResult with one line fromGestational week

    Covers below-3rd, exact threshold, between bins, and above-97th.
    Thresholds correspond to a single GA row: [3rd, 5th, 10th, 50th, 90th, 95th, 97th]
    """

    thresholds = [145.25, 147.25, 150.37, 161.95, 174.41, 178.12, 180.56]
    ga = GestationalAge.from_weeks(20.86)
    return ReferenceRange(gestational_age=ga, percentiles=thresholds)


@pytest.mark.parametrize(
    "value,expected_result",
    [
        (140.0, MeasurementResult.below_3p),
        (146.0, MeasurementResult.between_3p_5p),
        (149.0, MeasurementResult.between_5p_10p),
        (155.0, MeasurementResult.between_10p_50p),
        (165.0, MeasurementResult.between_50p_90p),
        (176.0, MeasurementResult.between_90p_95p),
        (179.0, MeasurementResult.between_95p_97p),
        (185.0, MeasurementResult.above_97p),
    ],
)
def test_reference_range_bins(ref_range: ReferenceRange, value: float, expected_result):
    """
    Verify percentile bin classification for all defined percentile ranges.
    """
    result = ref_range.evaluate(value)
    assert isinstance(result, MeasurementResult)
    assert result._lower == expected_result()._lower
    assert result._upper == expected_result()._upper
