"""
test_bpd_measurement.py

Integration tests for the BiparietalDiameterMeasurement class.
Uses NIHCD reference thresholds for BPD at 20.86 weeks (Non-Hispanic White)
to confirm correct percentile bin classification and (future) HPO term mapping.
"""

import pytest
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.measurement_result import MeasurementResult
from prenatalppkt.measurements.bpd_measurement import BiparietalDiameterMeasurement


@pytest.fixture
def reference_range() -> ReferenceRange:
    """
    NIHCD BPD reference thresholds at 20.86 weeks.
    Percentiles correspond to:
    [3rd, 5th, 10th, 50th, 90th, 95th, 97th]
    """
    thresholds = [145.25, 147.25, 150.37, 161.95, 174.41, 178.12, 180.56]
    ga = GestationalAge.from_weeks(20.86)
    return ReferenceRange(gestational_age=ga, percentiles=thresholds)


@pytest.mark.parametrize(
    "value, expected_bin",
    [
        (140.0, "below_3p"),
        (146.0, "between_3p_5p"),
        (149.0, "between_5p_10p"),
        (155.0, "between_10p_50p"),
        (170.0, "between_50p_90p"),
        (176.0, "between_90p_95p"),
        (179.0, "between_95p_97p"),
        (185.0, "above_97p"),
    ],
)
def test_bpd_measurement_bins(reference_range, value, expected_bin):
    """
    Verify that BPD measurements at 20.86 weeks are correctly
    classified into percentile bins according to NIHCD thresholds.
    """
    bpd = BiparietalDiameterMeasurement()
    ga = reference_range.gestational_age
    result = bpd.evaluate(ga, value, reference_range)
    assert isinstance(result, MeasurementResult)
    assert result.bin_key == expected_bin
