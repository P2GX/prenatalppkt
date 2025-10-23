"""
tests/test_phenotypic_export.py

Key design principles:
- Tests validate that YAML mappings are correctly applied
- No hardcoded HPO terms (except in YAML validation tests)
- Changes to biometry_hpo_mappings.yaml don't break tests
- Tests focus on the mapping logic, not specific term choices
"""

import json
import pytest
import yaml
from pathlib import Path
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


@pytest.fixture(scope="module")
def test_ga():
    """Use GA=14.0w - well-covered in INTERGROWTH reference data."""
    return 14.0


@pytest.fixture(scope="module")
def yaml_mappings():
    """Load the YAML mappings file for validation."""
    yaml_path = (
        Path(__file__).parent.parent
        / "data"
        / "mappings"
        / "biometry_hpo_mappings.yaml"
    )
    with open(yaml_path) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------- #
# HELPER FUNCTIONS
# ---------------------------------------------------------------------- #


def get_feature(exporter, measurement_type, value, ga=14.0, **kwargs):
    """Convenience wrapper: evaluate -> serialize."""
    obs = exporter.evaluate_to_observation(
        measurement_type=measurement_type,
        value_mm=value,
        gestational_age_weeks=ga,
        **kwargs,
    )
    assert isinstance(obs, TermObservation), "Must return TermObservation"
    return obs.to_phenotypic_feature()


def get_reference_values(exporter, measurement_type, ga):
    """Extract actual percentile thresholds from reference data.

    Returns dict with keys like "3rd", "5th", "10th", "50th", "90th", "95th", "97th"
    (WITHOUT "Percentile" suffix in INTERGROWTH data)
    """
    df = exporter.reference.tables[measurement_type]["ct"]
    row = df.loc[df["Gestational Age (weeks)"].round(1) == round(ga, 1)]
    if row.empty:
        raise ValueError(f"No reference data for {measurement_type} at GA={ga}w")

    # Get all percentile columns using case-insensitive check
    exclude_cols = {
        "Gestational Age (weeks)",
        "Measure",
        "Race",
        "SourceFile",
        "ParseTimestamp",
    }
    percentile_cols = [
        c for c in df.columns if c not in exclude_cols and "percentile" in c.lower()
    ]

    result = row[percentile_cols].iloc[0].to_dict()

    # Normalize keys: remove " Percentile" suffix if present for consistency
    normalized = {}
    for k, v in result.items():
        normalized_key = k.replace(" Percentile", "")
        normalized[normalized_key] = v

    return normalized


def get_expected_hpo(yaml_mappings, measurement_type, bin_key):
    """Get expected HPO term for a measurement type and bin from YAML."""
    mtype_config = yaml_mappings[measurement_type]
    bin_config = mtype_config["bins"].get(bin_key)

    if bin_config is None:
        return None

    return {"id": bin_config["id"], "label": bin_config["label"]}


# ---------------------------------------------------------------------- #
# INITIALIZATION TESTS
# ---------------------------------------------------------------------- #


def test_exporter_initialization(intergrowth_exporter):
    """Verify proper initialization with reference tables and YAML mappings."""
    assert intergrowth_exporter.source == "intergrowth"
    assert hasattr(intergrowth_exporter, "reference")
    assert hasattr(intergrowth_exporter, "mappings")

    expected_keys = {
        "head_circumference",
        "biparietal_diameter",
        "femur_length",
        "abdominal_circumference",
        "occipitofrontal_diameter",
    }
    assert expected_keys.issubset(intergrowth_exporter.mappings.keys())
    assert all(k in intergrowth_exporter.reference.tables for k in expected_keys)


def test_invalid_source_raises_error():
    """Invalid source should raise ValueError during initialization."""
    with pytest.raises(ValueError, match="Unsupported source"):
        PhenotypicExporter(source="invalid_source")


def test_mappings_structure(intergrowth_exporter):
    """Validate YAML mapping structure for all measurements."""
    for config in intergrowth_exporter.mappings.values():
        assert "bins" in config
        assert "normal_bins" in config
        assert "abnormal_term" in config
        assert isinstance(config["normal_bins"], set)
        assert "between_10p_50p" in config["normal_bins"]
        assert "between_50p_90p" in config["normal_bins"]


def test_fractional_gestational_age(intergrowth_exporter):
    """Fractional GA should round to nearest reference table row."""
    obs = intergrowth_exporter.evaluate_to_observation(
        "head_circumference", 100.0, 14.3
    )
    f = obs.to_phenotypic_feature()
    assert "14w" in f["description"]
    assert "type" in f


# ---------------------------------------------------------------------- #
# YAML-DRIVEN BIN MAPPING TESTS
# ---------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "measurement_type",
    [
        "head_circumference",
        "biparietal_diameter",
        "femur_length",
        "abdominal_circumference",
        "occipitofrontal_diameter",
    ],
)
def test_below_3p_maps_correctly(
    intergrowth_exporter, yaml_mappings, measurement_type, test_ga
):
    """Values below 3rd percentile should map to YAML-defined term for below_3p bin."""
    refs = get_reference_values(intergrowth_exporter, measurement_type, test_ga)
    value = refs["3rd"] - 1.0  # Below 3rd percentile

    expected_hpo = get_expected_hpo(yaml_mappings, measurement_type, "below_3p")

    f = get_feature(intergrowth_exporter, measurement_type, value, test_ga)

    if expected_hpo is None:
        # If YAML maps to null, should show abnormal_term with excluded=False
        abnormal_term = yaml_mappings[measurement_type]["abnormal_term"]
        assert f["type"]["id"] == abnormal_term["id"]
        assert f["excluded"] is False
    else:
        assert f["type"]["id"] == expected_hpo["id"]
        assert f["type"]["label"] == expected_hpo["label"]
        assert f["excluded"] is False


@pytest.mark.parametrize(
    "measurement_type",
    [
        "head_circumference",
        "biparietal_diameter",
        "femur_length",
        "abdominal_circumference",
        "occipitofrontal_diameter",
    ],
)
def test_between_3p_5p_maps_correctly(
    intergrowth_exporter, yaml_mappings, measurement_type, test_ga
):
    """Values between 3rd-5th percentile should map to YAML-defined term."""
    refs = get_reference_values(intergrowth_exporter, measurement_type, test_ga)
    value = (refs["3rd"] + refs["5th"]) / 2

    expected_hpo = get_expected_hpo(yaml_mappings, measurement_type, "between_3p_5p")

    f = get_feature(intergrowth_exporter, measurement_type, value, test_ga)

    if expected_hpo is None:
        # If YAML maps to null for this bin, result depends on normal_bins config
        normal_bins = yaml_mappings[measurement_type]["normal_bins"]
        if "between_3p_5p" in normal_bins:
            assert f["excluded"] is True
        else:
            abnormal_term = yaml_mappings[measurement_type]["abnormal_term"]
            assert f["type"]["id"] == abnormal_term["id"]
            assert f["excluded"] is False
    else:
        assert f["type"]["id"] == expected_hpo["id"]
        assert f["type"]["label"] == expected_hpo["label"]
        assert f["excluded"] is False


@pytest.mark.parametrize(
    "measurement_type",
    [
        "head_circumference",
        "biparietal_diameter",
        "femur_length",
        "abdominal_circumference",
        "occipitofrontal_diameter",
    ],
)
def test_normal_range_excluded(
    intergrowth_exporter, yaml_mappings, measurement_type, test_ga
):
    """Values in 10th-90th percentile should be excluded (normal)."""
    refs = get_reference_values(intergrowth_exporter, measurement_type, test_ga)
    value = refs["50th"]  # Dead center of normal range

    f = get_feature(intergrowth_exporter, measurement_type, value, test_ga)
    assert f["excluded"] is True
    assert "normal range" in f["description"].lower()


@pytest.mark.parametrize(
    "measurement_type",
    [
        "head_circumference",
        "biparietal_diameter",
        "femur_length",
        "abdominal_circumference",
        "occipitofrontal_diameter",
    ],
)
def test_above_97p_maps_correctly(
    intergrowth_exporter, yaml_mappings, measurement_type, test_ga
):
    """>97th percentile should map to YAML-defined term for above_97p bin."""
    refs = get_reference_values(intergrowth_exporter, measurement_type, test_ga)
    value = refs["97th"] + 1.0

    expected_hpo = get_expected_hpo(yaml_mappings, measurement_type, "above_97p")

    f = get_feature(intergrowth_exporter, measurement_type, value, test_ga)

    if expected_hpo is None:
        # If YAML maps to null, should show abnormal_term with excluded=False
        abnormal_term = yaml_mappings[measurement_type]["abnormal_term"]
        assert f["type"]["id"] == abnormal_term["id"]
        assert f["excluded"] is False
    else:
        assert f["type"]["id"] == expected_hpo["id"]
        assert f["type"]["label"] == expected_hpo["label"]
        assert f["excluded"] is False


# ---------------------------------------------------------------------- #
# SPECIFIC BIN VALIDATION (HEAD CIRCUMFERENCE EXAMPLE)
# ---------------------------------------------------------------------- #


def test_hc_all_bins_match_yaml(intergrowth_exporter, yaml_mappings, test_ga):
    """Comprehensive validation that all HC bins map to correct YAML terms."""
    refs = get_reference_values(intergrowth_exporter, "head_circumference", test_ga)

    # Test each bin with appropriate value
    bin_test_values = {
        "below_3p": refs["3rd"] - 1.0,
        "between_3p_5p": (refs["3rd"] + refs["5th"]) / 2,
        "between_5p_10p": (refs["5th"] + refs["10th"]) / 2,
        "between_10p_50p": refs["50th"] - 5.0,
        "between_50p_90p": refs["50th"] + 5.0,
        "between_90p_95p": (refs["90th"] + refs["95th"]) / 2,
        "between_95p_97p": (refs["95th"] + refs["97th"]) / 2,
        "above_97p": refs["97th"] + 1.0,
    }

    yaml_hc = yaml_mappings["head_circumference"]
    normal_bins = yaml_hc["normal_bins"]

    for bin_key, test_value in bin_test_values.items():
        f = get_feature(intergrowth_exporter, "head_circumference", test_value, test_ga)
        expected_hpo = yaml_hc["bins"].get(bin_key)

        if bin_key in normal_bins:
            # Should be excluded (normal)
            assert f["excluded"] is True, f"Bin {bin_key} should be excluded"
        elif expected_hpo is None:
            # Null mapping → uses abnormal_term
            assert f["type"]["id"] == yaml_hc["abnormal_term"]["id"]
            assert f["excluded"] is False
        else:
            # Specific HPO term from YAML
            assert f["type"]["id"] == expected_hpo["id"]
            assert f["type"]["label"] == expected_hpo["label"]
            assert f["excluded"] is False


# ---------------------------------------------------------------------- #
# CUSTOM NORMAL BIN OVERRIDE
# ---------------------------------------------------------------------- #


def test_custom_normal_bins_override(intergrowth_exporter, test_ga):
    """Custom normal_bins should override default exclusion logic."""
    refs = get_reference_values(intergrowth_exporter, "head_circumference", test_ga)
    value = (refs["5th"] + refs["10th"]) / 2

    # Without override: abnormal (observed=True)
    f1 = get_feature(intergrowth_exporter, "head_circumference", value, test_ga)
    assert f1["excluded"] is False

    # With override: treat 5-10p as normal
    custom_bins = {"between_5p_10p", "between_10p_50p", "between_50p_90p"}
    f2 = get_feature(
        intergrowth_exporter,
        "head_circumference",
        value,
        test_ga,
        normal_bins=custom_bins,
    )
    assert f2["excluded"] is True


# ---------------------------------------------------------------------- #
# BATCH EXPORT + JSON
# ---------------------------------------------------------------------- #


def test_batch_export_multiple(intergrowth_exporter, yaml_mappings, test_ga):
    """Batch export should process multiple measurements successfully."""
    refs_hc = get_reference_values(intergrowth_exporter, "head_circumference", test_ga)
    refs_fl = get_reference_values(intergrowth_exporter, "femur_length", test_ga)

    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": refs_hc["3rd"] - 1.0,
            "gestational_age_weeks": test_ga,
        },
        {
            "measurement_type": "femur_length",
            "value_mm": refs_fl["3rd"] - 0.5,
            "gestational_age_weeks": test_ga,
        },
        {
            "measurement_type": "biparietal_diameter",
            "value_mm": 28.0,  # Likely normal at GA=14w
            "gestational_age_weeks": test_ga,
        },
    ]

    results = intergrowth_exporter.batch_export(measurements)
    assert len(results) == 3

    # Verify results match YAML expectations
    expected_hc = get_expected_hpo(yaml_mappings, "head_circumference", "below_3p")
    expected_fl = get_expected_hpo(yaml_mappings, "femur_length", "below_3p")

    assert results[0]["type"]["id"] == expected_hc["id"]
    assert results[1]["type"]["id"] == expected_fl["id"]
    assert "excluded" in results[2]


def test_batch_export_handles_errors(intergrowth_exporter, test_ga):
    """Batch export should continue after encountering invalid measurement."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 100.0,
            "gestational_age_weeks": test_ga,
        },
        {
            "measurement_type": "nonexistent_type",
            "value_mm": 25.0,
            "gestational_age_weeks": test_ga,
        },
        {
            "measurement_type": "femur_length",
            "value_mm": 10.0,
            "gestational_age_weeks": test_ga,
        },
    ]

    results = intergrowth_exporter.batch_export(measurements)
    assert len(results) == 3
    assert "error" in results[1]
    assert "type" in results[0] and "type" in results[2]


def test_to_json_export(intergrowth_exporter, yaml_mappings, test_ga):
    """JSON export should produce valid, parseable JSON string."""
    refs_hc = get_reference_values(intergrowth_exporter, "head_circumference", test_ga)
    refs_fl = get_reference_values(intergrowth_exporter, "femur_length", test_ga)

    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": refs_hc["97th"] + 1.0,
            "gestational_age_weeks": test_ga,
        },
        {
            "measurement_type": "femur_length",
            "value_mm": refs_fl["50th"],
            "gestational_age_weeks": test_ga,
        },
    ]

    json_str = intergrowth_exporter.to_json(measurements)
    parsed = json.loads(json_str)
    assert isinstance(parsed, list)

    # Verify JSON output matches YAML expectations
    expected_hc = get_expected_hpo(yaml_mappings, "head_circumference", "above_97p")
    assert parsed[0]["type"]["id"] == expected_hc["id"]
    assert parsed[1]["excluded"] is True


def test_json_export_pretty_formatting(intergrowth_exporter, test_ga):
    """JSON export with pretty=True should be indented."""
    measurements = [
        {
            "measurement_type": "head_circumference",
            "value_mm": 100.0,
            "gestational_age_weeks": test_ga,
        }
    ]

    json_str = intergrowth_exporter.to_json(measurements, pretty=True)
    assert "\n" in json_str
    assert "  " in json_str  # Indentation


# ---------------------------------------------------------------------- #
# NICHD DATA SOURCE
# ---------------------------------------------------------------------- #


def test_nichd_reference_data(nichd_exporter, yaml_mappings):
    """NICHD exporter should operate similarly to INTERGROWTH."""
    # Use GA well-covered in NICHD data (e.g., 20w)
    ga = 20.0
    refs = get_reference_values(nichd_exporter, "head_circumference", ga)
    value = refs["3rd"] - 1.0

    expected_hpo = get_expected_hpo(yaml_mappings, "head_circumference", "below_3p")

    f = get_feature(nichd_exporter, "head_circumference", value, ga)
    assert f["excluded"] is False
    assert f["type"]["id"] == expected_hpo["id"]
    assert "20w" in f["description"]


def test_nichd_consistency_with_intergrowth(nichd_exporter, yaml_mappings):
    """NICHD and INTERGROWTH should use same mapping logic."""
    ga = 20.0

    # Get NICHD reference
    refs_nichd = get_reference_values(nichd_exporter, "femur_length", ga)
    value = refs_nichd["3rd"] - 0.5

    expected_hpo = get_expected_hpo(yaml_mappings, "femur_length", "below_3p")

    f_nichd = get_feature(nichd_exporter, "femur_length", value, ga)
    assert f_nichd["type"]["id"] == expected_hpo["id"]
    assert f_nichd["excluded"] is False


# ---------------------------------------------------------------------- #
# ERROR HANDLING
# ---------------------------------------------------------------------- #


def test_invalid_measurement_type_raises(intergrowth_exporter):
    """Unregistered measurement type should raise ValueError."""
    with pytest.raises(ValueError, match="not available"):
        intergrowth_exporter.evaluate_to_observation("unknown_measurement", 25.0, 14.0)


def test_invalid_ga_raises(intergrowth_exporter):
    """GA outside reference range should raise ValueError."""
    with pytest.raises(ValueError, match="No reference data"):
        intergrowth_exporter.evaluate_to_observation("head_circumference", 90.0, 2.0)


def test_missing_measurement_in_registry_raises(intergrowth_exporter):
    """Measurement type not in SonographicMeasurement.registry should raise KeyError."""
    # This would only happen if YAML has a type not backed by a subclass
    with pytest.raises((KeyError, ValueError)):
        intergrowth_exporter.evaluate_to_observation(
            "hypothetical_unregistered_type", 100.0, 14.0
        )


# ---------------------------------------------------------------------- #
# REGISTRY INTEGRATION TESTS
# ---------------------------------------------------------------------- #


def test_registry_based_dispatch(intergrowth_exporter):
    """Verify registry-based polymorphism works for all measurement types."""
    from prenatalppkt.sonographic_measurement import SonographicMeasurement

    for mtype in intergrowth_exporter.mappings:
        assert mtype in SonographicMeasurement.registry, (
            f"{mtype} missing from SonographicMeasurement registry"
        )

        # Instantiate and verify it has evaluate method
        cls = SonographicMeasurement.registry[mtype]
        instance = cls()
        assert hasattr(instance, "evaluate")


def test_evaluate_returns_measurement_result(intergrowth_exporter, test_ga):
    """Subclass.evaluate() must return MeasurementResult (not TermObservation)."""
    from prenatalppkt.measurements.measurement_result import MeasurementResult
    from prenatalppkt.sonographic_measurement import SonographicMeasurement
    from prenatalppkt.measurements.reference_range import ReferenceRange
    from prenatalppkt.gestational_age import GestationalAge

    refs = get_reference_values(intergrowth_exporter, "head_circumference", test_ga)
    ga = GestationalAge.from_weeks(test_ga)
    ref_range = ReferenceRange(ga, list(refs.values()))

    cls = SonographicMeasurement.registry["head_circumference"]
    instance = cls()
    result = instance.evaluate(ga, refs["50th"], ref_range)

    assert isinstance(result, MeasurementResult), (
        "Subclass.evaluate() must return MeasurementResult"
    )


# ---------------------------------------------------------------------- #
# SEPARATION OF CONCERNS
# ---------------------------------------------------------------------- #


def test_evaluate_vs_export_separation(intergrowth_exporter, test_ga):
    """evaluate_to_observation returns TermObservation; export_feature returns dict."""
    obs = intergrowth_exporter.evaluate_to_observation(
        "head_circumference", 100.0, test_ga
    )
    assert isinstance(obs, TermObservation)

    feature_dict = intergrowth_exporter.export_feature(
        "head_circumference", 100.0, test_ga
    )
    assert isinstance(feature_dict, dict)
    assert "type" in feature_dict
    assert "excluded" in feature_dict


def test_all_measurements_supported(intergrowth_exporter):
    """Every measurement in YAML should be evaluatable without crashes."""
    test_ga = 14.0
    for mtype in intergrowth_exporter.mappings:
        obs = None
        try:
            obs = intergrowth_exporter.evaluate_to_observation(mtype, 100.0, test_ga)
        except ValueError:
            # Some measurements might not have data at GA=14w, that's OK
            continue
        f = obs.to_phenotypic_feature()
        assert isinstance(f, dict)
        assert "excluded" in f
