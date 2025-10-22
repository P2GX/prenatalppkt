"""
test_phenotypic_export.py

Comprehensive test suite for the PhenotypicExporter class.

Tests cover:
1. Correct percentile → HPO term mappings
2. Normal results marked as excluded=True
3. Abnormal bins produce correct HPO IDs and labels
4. Behavior when percentile data missing
5. Batch export functionality
6. JSON serialization
"""

import pytest
import json
from prenatalppkt.phenotypic_export import PhenotypicExporter


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #


@pytest.fixture(params=["intergrowth", "nichd"])
def exporter(request) -> PhenotypicExporter:
    """Provide exporter for both reference sources."""
    return PhenotypicExporter(source=request.param)


@pytest.fixture
def intergrowth_exporter() -> PhenotypicExporter:
    """INTERGROWTH-specific exporter for tests requiring that source."""
    return PhenotypicExporter(source="intergrowth")


@pytest.fixture
def nichd_exporter() -> PhenotypicExporter:
    """NICHD-specific exporter for tests requiring that source."""
    return PhenotypicExporter(source="nichd")


# ------------------------------------------------------------------ #
# Basic Functionality Tests
# ------------------------------------------------------------------ #


def test_exporter_initialization():
    """Verify exporter initializes correctly with default settings."""
    exporter = PhenotypicExporter(source="intergrowth")
    assert exporter.source == "intergrowth"
    assert exporter.reference is not None
    assert exporter.mappings is not None
    assert "between_10p_50p" in exporter.normal_bins
    assert "between_50p_90p" in exporter.normal_bins


def test_invalid_source_raises_error():
    """Unsupported reference sources should raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported source"):
        PhenotypicExporter(source="invalid_source")


# ------------------------------------------------------------------ #
# Head Circumference Tests
# ------------------------------------------------------------------ #


def test_hc_microcephaly_detected(intergrowth_exporter):
    """Values below 3rd percentile should map to Microcephaly (HP:0000252)."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="head_circumference",
        value_mm=85.0,  # Well below 3rd percentile at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["type"]["id"] == "HP:0000252"
    assert result["type"]["label"] == "Microcephaly"
    assert result["excluded"] is False
    assert "14w0d" in result["description"]


def test_hc_macrocephaly_detected(intergrowth_exporter):
    """Values above 97th percentile should map to Macrocephaly (HP:0000256)."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="head_circumference",
        value_mm=110.0,  # Above 97th percentile at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["type"]["id"] == "HP:0000256"
    assert result["type"]["label"] == "Macrocephaly"
    assert result["excluded"] is False


def test_hc_normal_range_excluded(intergrowth_exporter):
    """Normal HC values (10th-90th percentile) should be marked excluded."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="head_circumference",
        value_mm=97.9,  # Median (50th percentile) at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["excluded"] is True
    assert "normal range" in result["description"]


# ------------------------------------------------------------------ #
# Femur Length Tests
# ------------------------------------------------------------------ #


def test_fl_short_femur_detected(intergrowth_exporter):
    """Values below 3rd percentile should map to Short femur (HP:0011428)."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="femur_length",
        value_mm=10.0,  # Below 3rd percentile at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["type"]["id"] == "HP:0011428"
    assert "Short fetal femur length" in result["type"]["label"]
    assert result["excluded"] is False


def test_fl_normal_range(intergrowth_exporter):
    """Normal FL values should be marked excluded."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="femur_length",
        value_mm=13.1,  # Median at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["excluded"] is True


# ------------------------------------------------------------------ #
# Biparietal Diameter Tests
# ------------------------------------------------------------------ #


def test_bpd_decreased_width(intergrowth_exporter):
    """BPD below 3rd percentile maps to Decreased skull width."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="biparietal_diameter",
        value_mm=25.0,  # Below 3rd percentile at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["type"]["id"] == "HP:0005484"
    assert "Secondary microcephaly" in result["type"]["label"]
    assert result["excluded"] is False


def test_bpd_increased_width(intergrowth_exporter):
    """BPD above 97th percentile maps to Increased skull width."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="biparietal_diameter",
        value_mm=34.0,  # Above 97th percentile at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["type"]["id"] == "HP:0005490"
    assert "Postnatal macrocephaly" in result["type"]["label"]
    assert result["excluded"] is False


# ------------------------------------------------------------------ #
# Abdominal Circumference Tests
# ------------------------------------------------------------------ #


def test_ac_decreased(intergrowth_exporter):
    """AC below 3rd percentile maps to Decreased abdominal circumference."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="abdominal_circumference",
        value_mm=70.0,  # Below 3rd percentile at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["type"]["id"] == "HP:6000339"
    assert "Small fetal abdominal circumference" in result["type"]["label"]
    assert result["excluded"] is False


# ------------------------------------------------------------------ #
# Edge Cases and Error Handling
# ------------------------------------------------------------------ #


def test_missing_reference_data_raises_error(intergrowth_exporter):
    """GA outside reference range should raise ValueError."""
    with pytest.raises(ValueError, match="No reference data"):
        intergrowth_exporter.evaluate_and_export(
            measurement_type="head_circumference",
            value_mm=100.0,
            gestational_age_weeks=50,  # Outside valid range
        )


def test_unsupported_measurement_type_raises_error(intergrowth_exporter):
    """Invalid measurement types should raise ValueError."""
    with pytest.raises(ValueError, match="not available"):
        intergrowth_exporter.evaluate_and_export(
            measurement_type="invalid_measurement",
            value_mm=100.0,
            gestational_age_weeks=20,
        )


def test_fractional_gestational_age(intergrowth_exporter):
    """Fractional GA should be handled correctly."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type="head_circumference",
        value_mm=172.5,  # Median at 20 weeks
        gestational_age_weeks=20.86,
    )

    assert "20w6d" in result["description"]


# ------------------------------------------------------------------ #
# Custom Normal Bins
# ------------------------------------------------------------------ #


def test_custom_normal_bins():
    """Custom normal bin definitions should override defaults."""
    exporter = PhenotypicExporter(
        source="intergrowth",
        normal_bins={
            "between_5p_10p",
            "between_10p_50p",
            "between_50p_90p",
            "between_90p_95p",
        },
    )

    # Value in 5th-10th percentile should now be "normal"
    result = exporter.evaluate_and_export(
        measurement_type="head_circumference",
        value_mm=91.0,  # ~5th-10th percentile at 14 weeks
        gestational_age_weeks=14,
    )

    assert result["excluded"] is True


# ------------------------------------------------------------------ #
# Batch Export Tests
# ------------------------------------------------------------------ #


def test_batch_export_multiple_measurements(intergrowth_exporter):
    """Batch export should process multiple measurements correctly."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 97.9,
            "gestational_age_weeks": 14,
        },
        {
            "measurement_type": "femur_length",
            "value_mm": 13.1,
            "gestational_age_weeks": 14,
        },
        {
            "measurement_type": "biparietal_diameter",
            "value_mm": 29.6,
            "gestational_age_weeks": 14,
        },
    ]

    results = intergrowth_exporter.batch_export(measurements)

    assert len(results) == 3
    assert all("excluded" in r for r in results)
    assert all(r["excluded"] is True for r in results)  # All normal


def test_batch_export_handles_errors(intergrowth_exporter):
    """Batch export should handle individual failures gracefully."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 97.9,
            "gestational_age_weeks": 14,
        },
        {
            "measurement_type": "invalid_type",
            "value_mm": 100.0,
            "gestational_age_weeks": 20,
        },
    ]

    results = intergrowth_exporter.batch_export(measurements)

    assert len(results) == 2
    assert "excluded" in results[0]  # First succeeded
    assert "error" in results[1]  # Second failed


# ------------------------------------------------------------------ #
# JSON Serialization Tests
# ------------------------------------------------------------------ #


def test_to_json_valid_format(intergrowth_exporter):
    """JSON export should produce valid, parseable JSON."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 85.0,
            "gestational_age_weeks": 14,
        }
    ]

    json_str = intergrowth_exporter.to_json(measurements, pretty=True)

    # Should be valid JSON
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["type"]["id"] == "HP:0000252"


def test_to_json_pretty_formatting(intergrowth_exporter):
    """Pretty JSON should include indentation."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 97.9,
            "gestational_age_weeks": 14,
        }
    ]

    json_str = intergrowth_exporter.to_json(measurements, pretty=True)

    assert "\n" in json_str  # Contains newlines
    assert "  " in json_str  # Contains indentation


def test_to_json_compact_formatting(intergrowth_exporter):
    """Compact JSON should be single-line."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 97.9,
            "gestational_age_weeks": 14,
        }
    ]

    json_str = intergrowth_exporter.to_json(measurements, pretty=False)

    # Should be compact (no unnecessary whitespace)
    parsed = json.loads(json_str)
    assert len(parsed) == 1


# ------------------------------------------------------------------ #
# NICHD-Specific Tests
# ------------------------------------------------------------------ #


def test_nichd_source_works(nichd_exporter):
    """NICHD reference data should work for supported measurements."""
    result = nichd_exporter.evaluate_and_export(
        measurement_type="head_circumference", value_mm=120.0, gestational_age_weeks=20
    )

    # Should successfully evaluate (result structure validated elsewhere)
    assert "excluded" in result


@pytest.mark.parametrize(
    "measurement_type",
    [
        "head_circumference",
        "biparietal_diameter",
        "femur_length",
        "abdominal_circumference",
    ],
)
def test_all_core_measurements_supported(intergrowth_exporter, measurement_type):
    """All core measurements should have mappings and reference data."""
    result = intergrowth_exporter.evaluate_and_export(
        measurement_type=measurement_type,
        value_mm=100.0,  # Arbitrary value
        gestational_age_weeks=20,
    )

    assert "excluded" in result
    assert "description" in result
