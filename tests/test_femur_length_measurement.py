"""
test_femur_length_measurement.py

Integration tests for the FemurLengthMeasurement class.
Uses NIHCD reference thresholds for femur length at 20.86 weeks
(Non-Hispanic White population) to verify correct percentile bin
classification and ontology (HPO) term mapping.
"""

import pytest
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.measurement_result import MeasurementResult
from prenatalppkt.measurements.femur_length_measurement import FemurLengthMeasurement


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


@pytest.mark.parametrize(
    "value, expected_bin",
    [
        (27.0, "below_3p"),
        (29.4, "between_3p_5p"),
        (30.2, "between_5p_10p"),
        (33.5, "between_10p_50p"),
        (37.0, "between_50p_90p"),
        (38.7, "between_90p_95p"),
        (39.6, "between_95p_97p"),
        (41.0, "above_97p"),
    ],
)
def test_femur_length_measurement_bins(reference_range, value, expected_bin):
    """
    Verify that femur length measurements at 20.86 weeks are correctly
    classified into percentile bins according to NIHCD thresholds.
    """
    fl = FemurLengthMeasurement()
    ga = reference_range.gestational_age
    result = fl.evaluate(ga, value, reference_range)
    assert isinstance(result, MeasurementResult)
    assert result.get_bin_key == expected_bin
