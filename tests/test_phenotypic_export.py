"""
tests/test_phenotypic_export.py

Comprehensive test suite for PhenotypicExporter.

Ensures correct:
- YAML-based HPO term mapping
- Normal vs abnormal logic (observed/excluded)
- Custom normal bin overrides
- Batch and JSON export
- Compatibility with INTERGROWTH and NICHD sources
- Initialization and error-handling behavior
"""

import json
import pytest
from prenatalppkt.phenotypic_export import PhenotypicExporter
from prenatalppkt.term_observation import TermObservation


# ---------------------------------------------------------------------- #
# FIXTURES
# ---------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def intergrowth_exporter():
    return PhenotypicExporter(source="intergrowth")


@pytest.fixture(scope="module")
def nichd_exporter():
    return PhenotypicExporter(source="nichd")


# ---------------------------------------------------------------------- #
# INITIALIZATION + BASIC SANITY CHECKS
# ---------------------------------------------------------------------- #


def test_exporter_initialization(intergrowth_exporter):
    """Exporter initializes with proper reference tables and mappings."""
    assert intergrowth_exporter.source == "intergrowth"
    assert hasattr(intergrowth_exporter, "reference")
    assert hasattr(intergrowth_exporter, "mappings")
    assert isinstance(intergrowth_exporter.mappings, dict)
    # Check at least the five core measurement types are present
    expected_keys = {
        "head_circumference",
        "biparietal_diameter",
        "femur_length",
        "abdominal_circumference",
        "occipitofrontal_diameter",
    }
    assert expected_keys.issubset(intergrowth_exporter.mappings.keys())
    # Reference tables must include these too
    assert all(k in intergrowth_exporter.reference.tables for k in expected_keys)


def test_invalid_source_raises_error():
    """Invalid exporter source should raise a ValueError."""
    with pytest.raises(ValueError):
        PhenotypicExporter(source="invalid_source_name")


def test_fractional_gestational_age(intergrowth_exporter):
    """Fractional gestational ages (e.g. 14.3w) should round correctly to reference table rows."""
    f = intergrowth_exporter.evaluate_to_observation(
        "head_circumference", 100.0, 14.3
    ).to_phenotypic_feature()
    assert "14w" in f["description"]
    assert "type" in f and "label" in f["type"]


def test_batch_export_handles_errors(intergrowth_exporter):
    """Batch export should continue processing after an invalid measurement."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 85.0,
            "gestational_age_weeks": 14.0,
        },
        {
            "measurement_type": "nonexistent_type",
            "value_mm": 25.0,
            "gestational_age_weeks": 14.0,
        },
        {
            "measurement_type": "femur_length",
            "value_mm": 7.0,
            "gestational_age_weeks": 14.0,
        },
    ]
    result = intergrowth_exporter.batch_export(measurements)
    assert len(result) == 3
    assert "error" in result[1]
    assert "type" in result[0] and "type" in result[2]


def test_all_core_measurements_supported(intergrowth_exporter):
    """Ensure every core measurement type in YAML can be evaluated without crash."""
    for mtype in intergrowth_exporter.mappings.keys():
        obs = intergrowth_exporter.evaluate_to_observation(mtype, 100.0, 14.0)
        f = obs.to_phenotypic_feature()
        assert isinstance(f, dict)
        assert "excluded" in f


# ---------------------------------------------------------------------- #
# HELPER
# ---------------------------------------------------------------------- #


def get_feature(exporter, measurement_type, value, ga=14.0, **kwargs):
    """Convenience wrapper to obtain serialized feature."""
    obs = exporter.evaluate_to_observation(
        measurement_type=measurement_type,
        value_mm=value,
        gestational_age_weeks=ga,
        **kwargs,
    )
    assert isinstance(obs, TermObservation)
    return obs.to_phenotypic_feature()


# ---------------------------------------------------------------------- #
# HEAD CIRCUMFERENCE (HC)
# ---------------------------------------------------------------------- #


def test_hc_lower_extreme_microcephaly(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "head_circumference", 85.0)
    assert f["type"]["id"] == "HP:0000252"
    assert f["type"]["label"] == "Microcephaly"
    assert f["excluded"] is False


def test_hc_lower_decreased_head_circumference(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "head_circumference", 88.0)
    assert f["type"]["label"] == "Decreased head circumference"
    assert f["excluded"] is False


def test_hc_normal_excluded(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "head_circumference", 100.0)
    assert f["excluded"] is True
    assert "normal range" in f["description"]


def test_hc_upper_increased_head_circumference(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "head_circumference", 115.0)
    assert f["type"]["label"] == "Increased head circumference"
    assert f["excluded"] is False


def test_hc_upper_extreme_macrocephaly(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "head_circumference", 120.0)
    assert f["type"]["label"] == "Macrocephaly"
    assert f["excluded"] is False


# ---------------------------------------------------------------------- #
# BIPARIETAL DIAMETER (BPD)
# ---------------------------------------------------------------------- #


def test_bpd_lower_extreme_secondary_microcephaly(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "biparietal_diameter", 20.0)
    assert f["type"]["label"] == "Secondary microcephaly"
    assert f["excluded"] is False


def test_bpd_abnormal_skull_size(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "biparietal_diameter", 23.0)
    assert f["type"]["label"] == "Abnormality of skull size"
    assert f["excluded"] is False


def test_bpd_upper_postnatal_macrocephaly(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "biparietal_diameter", 45.0)
    assert f["type"]["label"] == "Postnatal macrocephaly"
    assert f["excluded"] is False


def test_bpd_normal_excluded(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "biparietal_diameter", 28.0)
    assert f["excluded"] is True


# ---------------------------------------------------------------------- #
# FEMUR LENGTH (FL)
# ---------------------------------------------------------------------- #


def test_fl_lower_extreme_short_fetal_femur(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "femur_length", 5.0)
    assert f["type"]["label"] == "Short fetal femur length"
    assert f["excluded"] is False


def test_fl_lower_short_femur(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "femur_length", 6.0)
    assert f["type"]["label"] == "Short femur"
    assert f["excluded"] is False


def test_fl_abnormal_morphology(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "femur_length", 7.0)
    assert f["type"]["label"] == "Abnormal femur morphology"
    assert f["excluded"] is False


def test_fl_normal_excluded(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "femur_length", 8.0)
    assert f["excluded"] is True


# ---------------------------------------------------------------------- #
# ABDOMINAL CIRCUMFERENCE (AC)
# ---------------------------------------------------------------------- #


def test_ac_lower_extreme_small_abdomen(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "abdominal_circumference", 60.0)
    assert f["type"]["label"] == "Small fetal abdominal circumference"
    assert f["excluded"] is False


def test_ac_abnormal_gi_morphology(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "abdominal_circumference", 65.0)
    assert f["type"]["label"] == "Abnormal fetal gastrointestinal system morphology"
    assert f["excluded"] is False


def test_ac_normal_excluded(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "abdominal_circumference", 90.0)
    assert f["excluded"] is True


# ---------------------------------------------------------------------- #
# OCCIPITOFRONTAL DIAMETER (OFD)
# ---------------------------------------------------------------------- #


def test_ofd_abnormal_skull(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "occipitofrontal_diameter", 25.0)
    assert f["type"]["label"] == "Abnormality of skull size"
    assert f["excluded"] is False


def test_ofd_normal_excluded(intergrowth_exporter):
    f = get_feature(intergrowth_exporter, "occipitofrontal_diameter", 35.0)
    assert f["excluded"] is True


# ---------------------------------------------------------------------- #
# NORMAL BIN OVERRIDE
# ---------------------------------------------------------------------- #


def test_custom_normal_bins_override(intergrowth_exporter):
    """User-defined normal bins should override defaults."""
    custom_bins = {"between_5p_10p"}  # treat 5-10th percentile as normal
    obs = intergrowth_exporter.evaluate_to_observation(
        "head_circumference", 90.0, 14.0, normal_bins=custom_bins
    )
    f = obs.to_phenotypic_feature()
    assert f["excluded"] is True  # normally abnormal, now excluded


# ---------------------------------------------------------------------- #
# BATCH EXPORT + JSON
# ---------------------------------------------------------------------- #


def test_batch_export_multiple(intergrowth_exporter):
    """Batch export should process multiple measurements successfully."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 85.0,
            "gestational_age_weeks": 14.0,
        },
        {
            "measurement_type": "femur_length",
            "value_mm": 5.0,
            "gestational_age_weeks": 14.0,
        },
        {
            "measurement_type": "biparietal_diameter",
            "value_mm": 20.0,
            "gestational_age_weeks": 14.0,
        },
    ]
    result = intergrowth_exporter.batch_export(measurements)
    assert isinstance(result, list)
    assert len(result) == 3
    labels = [r["type"]["label"] for r in result if "type" in r]
    assert "Microcephaly" in labels
    assert "Short fetal femur length" in labels


def test_to_json_export(intergrowth_exporter):
    """JSON export should yield valid and parseable JSON string."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 120.0,
            "gestational_age_weeks": 14.0,
        },
        {
            "measurement_type": "femur_length",
            "value_mm": 8.0,
            "gestational_age_weeks": 14.0,
        },
    ]
    json_str = intergrowth_exporter.to_json(measurements)
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert parsed[0]["type"]["label"] == "Macrocephaly"
    assert parsed[1]["excluded"] is True


# ---------------------------------------------------------------------- #
# NICHD DATA SOURCE
# ---------------------------------------------------------------------- #


def test_nichd_reference_data(nichd_exporter):
    """Ensure NICHD reference operates similarly for supported measurements."""
    f = get_feature(nichd_exporter, "head_circumference", 85.0)
    assert f["type"]["label"] in {"Microcephaly", "Abnormality of skull size"}
    assert "14w" in f["description"]


# ---------------------------------------------------------------------- #
# ERROR HANDLING
# ---------------------------------------------------------------------- #


def test_invalid_measurement_raises(intergrowth_exporter):
    with pytest.raises(ValueError):
        intergrowth_exporter.evaluate_to_observation("unknown_measurement", 25.0, 14.0)


def test_invalid_ga_raises(intergrowth_exporter):
    with pytest.raises(ValueError):
        intergrowth_exporter.evaluate_to_observation("head_circumference", 90.0, 2.0)
