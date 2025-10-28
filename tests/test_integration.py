"""
test_integration.py - Integration tests for the complete pipeline
"""

import pytest
from prenatalppkt.measurement_eval import MeasurementEvaluation
from prenatalppkt.gestational_age import GestationalAge


def test_end_to_end_hc_abnormal():
    """Test complete pipeline for abnormal HC measurement."""
    # Initialize evaluator
    evaluator = MeasurementEvaluation()

    # Get HC mapper
    hc_mapper = evaluator.get_measurement_mapper("head_circumference")
    assert hc_mapper is not None

    # Test abnormal percentile (4.3 falls in 3-5 range)
    ga = GestationalAge(20, 3)
    term_obs = hc_mapper.from_percentile(4.3, ga)

    assert term_obs.hpo_id == "HP:0040195"
    assert term_obs.hpo_label == "Decreased head circumference"
    assert term_obs.observed is True
    assert term_obs.percentile == 4.3
    assert term_obs.category == "lower_term"


def test_end_to_end_hc_normal():
    """Test complete pipeline for normal HC measurement."""
    evaluator = MeasurementEvaluation()
    hc_mapper = evaluator.get_measurement_mapper("head_circumference")

    # Test normal percentile (47.8 falls in 10-50 range)
    ga = GestationalAge(20, 3)
    term_obs = hc_mapper.from_percentile(47.8, ga)

    assert term_obs.hpo_id == "HP:0000240"
    assert term_obs.observed is False  # Excluded (normal)
    assert term_obs.category == "normal_term"


def test_all_measurements_available():
    """Test all measurement types are loaded."""
    evaluator = MeasurementEvaluation()
    measurements = evaluator.get_available_measurements()

    assert "head_circumference" in measurements
    assert "biparietal_diameter" in measurements
    assert "femur_length" in measurements
    assert "abdominal_circumference" in measurements
    assert "occipitofrontal_diameter" in measurements


def test_percentile_out_of_range():
    """Test error handling for invalid percentile."""
    evaluator = MeasurementEvaluation()
    hc_mapper = evaluator.get_measurement_mapper("head_circumference")

    ga = GestationalAge(20, 3)

    # Test percentile > 100 (should fail)
    with pytest.raises(ValueError, match="No HPO mapping"):
        hc_mapper.from_percentile(101, ga)
