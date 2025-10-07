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


@pytest.mark.parametrize(
    "value, expected_label, expected_observed",
    [
        (140.0, "Microcephaly", True),  # <=3rd
        (146.0, "Microcephaly", True),  # 3-5
        (149.0, "Abnormality of skull size", True),  # 5-10
        (155.0, None, False),  # 10-50 , no ontology term for "normal" percentiles
        (170.0, None, False),  # 50-90 , no ontology term for "normal" percentiles
        (176.0, "Abnormality of skull size", True),  # 90-95
        (179.0, "Macrocephaly", True),  # 95-97
        (185.0, "Macrocephaly", True),  # >=97
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
