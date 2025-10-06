import pytest
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.measurement_result import MeasurementResult
from prenatalppkt.measurements.reference_range import ReferenceRange


# -----------------------
# Shared fixtures
# -----------------------


@pytest.fixture
def reference(request) -> ReferenceRange:  # type: ignore
    """Create MeasurementResult with one line from
    Gestational week - 20.86,  Non-Hispanic White, Abdominal Circ
    """
    thresholds = [145.25, 147.25, 150.37, 161.95, 174.41, 178.12, 180.56]
    gestational_age = GestationalAge.from_weeks(20.86)
    ref_range = ReferenceRange(gestational_age=gestational_age, percentiles=thresholds)

    return ref_range


"""
@pytest.mark.parametrize(
    "value_mm, percentile_low, percentile_high",
    [
       ...
    ],
)
def test_measurement_result(value_mm: float, percentile_low: Percentile, percentile_high: Percentile):
 -- test all possibiliites, <3, exactly 3, 3-5, etc etc
"""
