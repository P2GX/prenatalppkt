"""
Tests for ETL constants and enums.
"""

import pytest
from prenatalppkt.etl.constants import (
    BiometryMeasurement,
    SectionHeader,
    normalize_measurement_name,
    is_target_measurement,
    OBSERVER_NAME_MAP,
    VIEWPOINT_TEXT_NAME_MAP,
    VIEWPOINT_HL7_NAME_MAP,
)


class TestBiometryMeasurement:
    """Tests for BiometryMeasurement enum."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        assert BiometryMeasurement.HEAD_CIRCUMFERENCE.value == "HC"
        assert BiometryMeasurement.BIPARIETAL_DIAMETER.value == "BPD"
        assert BiometryMeasurement.ABDOMINAL_CIRCUMFERENCE.value == "AC"
        assert BiometryMeasurement.FEMUR_LENGTH.value == "Femur"
        assert BiometryMeasurement.NUCHAL_FOLD.value == "Nuchal Fold"
        assert BiometryMeasurement.CEREBELLUM.value == "Cerebellum"
        assert BiometryMeasurement.OCCIPITOFRONTAL_DIAMETER.value == "OFD"
        assert BiometryMeasurement.HUMERUS_LENGTH.value == "Humerus"

    def test_from_string(self):
        """Test from_string class method."""
        hc = BiometryMeasurement.from_string("HC")
        assert hc == BiometryMeasurement.HEAD_CIRCUMFERENCE

        femur = BiometryMeasurement.from_string("Femur")
        assert femur == BiometryMeasurement.FEMUR_LENGTH

    def test_from_string_invalid(self):
        """Test from_string with invalid name."""
        with pytest.raises(ValueError, match="not a valid"):
            BiometryMeasurement.from_string("InvalidMeasurement")

    def test_all_values(self):
        """Test all_values returns all standard names."""
        values = BiometryMeasurement.all_values()
        assert isinstance(values, set)
        # 8 T2/T3 + 2 T1 (CRL, NT) + 11 newly-recognized labels
        assert len(values) == 21
        assert "HC" in values
        assert "BPD" in values
        assert "Femur" in values
        assert "CRL" in values
        assert "NT" in values
        assert "Tibia" in values
        assert "Fibula" in values
        assert "Radius" in values
        assert "Ulna" in values
        assert "Foot" in values
        assert "Cisterna Magna" in values
        assert "Nasal Bone" in values
        assert "Lateral Vent left" in values
        assert "Lateral Vent right" in values
        assert "Biorbit" in values
        assert "Mean Gest Sac" in values


class TestSectionHeader:
    """Tests for SectionHeader enum."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        assert SectionHeader.FETAL_BIOMETRY.value == "Fetal Biometry"
        assert SectionHeader.CLINICAL_IMPRESSION.value == "Impression"
        assert SectionHeader.PATIENT_HISTORY.value == "History"

    def test_from_string(self):
        """Test from_string class method."""
        section = SectionHeader.from_string("Fetal Biometry")
        assert section == SectionHeader.FETAL_BIOMETRY

    def test_from_string_invalid(self):
        """Test from_string with invalid section."""
        with pytest.raises(ValueError, match="not a valid"):
            SectionHeader.from_string("Invalid Section")


class TestNormalizeMeasurementName:
    """Tests for normalize_measurement_name function."""

    def test_normalize_exact_match(self):
        """Test normalization with exact match."""
        result = normalize_measurement_name("HC")
        assert result == "HC"

    def test_normalize_case_insensitive(self):
        """Test case-insensitive normalization."""
        result = normalize_measurement_name("hc")
        assert result == "HC"

        result = normalize_measurement_name("BPD")
        assert result == "BPD"

    def test_normalize_with_underscores(self):
        """Test normalization of names with underscores."""
        result = normalize_measurement_name("head_circumference")
        assert result == "HC"

        result = normalize_measurement_name("femur_length")
        assert result == "Femur"

    def test_normalize_with_spaces(self):
        """Test normalization of names with spaces."""
        result = normalize_measurement_name("nuchal fold")
        assert result == "Nuchal Fold"

    def test_normalize_hl7_format(self):
        """Test normalization of HL7 format names."""
        result = normalize_measurement_name("HeadCircumference", VIEWPOINT_HL7_NAME_MAP)
        assert result == "HC"

        result = normalize_measurement_name(
            "BiParietalDiameter", VIEWPOINT_HL7_NAME_MAP
        )
        assert result == "BPD"

    def test_normalize_observer_format(self):
        """Test normalization of Observer format names."""
        result = normalize_measurement_name("HC", OBSERVER_NAME_MAP)
        assert result == "HC"

        result = normalize_measurement_name("Femur", OBSERVER_NAME_MAP)
        assert result == "Femur"

        # Real Observer 7 exports emit "FL"; normalize to the standard "Femur".
        result = normalize_measurement_name("FL", OBSERVER_NAME_MAP)
        assert result == "Femur"

    def test_normalize_invalid_name(self):
        """Test that invalid names raise ValueError."""
        with pytest.raises(ValueError, match="Cannot normalize"):
            normalize_measurement_name("UnknownMeasurement")


class TestIsTargetMeasurement:
    """Tests for is_target_measurement function."""

    def test_is_target_valid(self):
        """Test with valid target measurements."""
        assert is_target_measurement("HC") is True
        assert is_target_measurement("hc") is True
        assert is_target_measurement("head_circumference") is True
        assert is_target_measurement("BPD") is True
        assert is_target_measurement("Femur") is True

    def test_is_target_invalid(self):
        """Test with invalid measurements."""
        assert is_target_measurement("UnknownMeasurement") is False
        assert is_target_measurement("random_string") is False

    def test_is_target_with_format_map(self):
        """Test with format-specific maps."""
        assert (
            is_target_measurement("HeadCircumference", VIEWPOINT_HL7_NAME_MAP) is True
        )
        assert is_target_measurement("HC", OBSERVER_NAME_MAP) is True


class TestNameMaps:
    """Tests for format-specific name maps."""

    def test_observer_map_completeness(self):
        """Test that Observer map has all measurements."""
        # 8 T2/T3 + 2 T1 (CRL, NT) + "FL" alias for Femur
        # + 11 newly-recognized labels
        assert len(OBSERVER_NAME_MAP) == 22
        assert "HC" in OBSERVER_NAME_MAP
        assert "BPD" in OBSERVER_NAME_MAP
        assert "Femur" in OBSERVER_NAME_MAP
        assert "FL" in OBSERVER_NAME_MAP
        assert "CRL" in OBSERVER_NAME_MAP
        assert "NT" in OBSERVER_NAME_MAP
        assert "Tibia" in OBSERVER_NAME_MAP
        assert "Fibula" in OBSERVER_NAME_MAP
        assert "Radius" in OBSERVER_NAME_MAP
        assert "Ulna" in OBSERVER_NAME_MAP
        assert "Foot" in OBSERVER_NAME_MAP
        assert "Cisterna Magna" in OBSERVER_NAME_MAP
        assert "Nasal Bone" in OBSERVER_NAME_MAP
        assert "Lateral Vent left" in OBSERVER_NAME_MAP
        assert "Lateral Vent right" in OBSERVER_NAME_MAP
        assert "Biorbit" in OBSERVER_NAME_MAP
        assert "Mean Gest Sac" in OBSERVER_NAME_MAP

    def test_viewpoint_text_map_completeness(self):
        """Test that ViewPoint text map has all measurements."""
        assert len(VIEWPOINT_TEXT_NAME_MAP) == 8
        assert "HC" in VIEWPOINT_TEXT_NAME_MAP
        assert "OFD" in VIEWPOINT_TEXT_NAME_MAP

    def test_viewpoint_hl7_map_completeness(self):
        """Test that ViewPoint HL7 map has all measurements."""
        assert len(VIEWPOINT_HL7_NAME_MAP) >= 8  # May have variations
        assert "HeadCircumference" in VIEWPOINT_HL7_NAME_MAP
        assert "BiParietalDiameter" in VIEWPOINT_HL7_NAME_MAP

    def test_maps_point_to_same_enums(self):
        """Test that all maps point to BiometryMeasurement enums."""
        for value in OBSERVER_NAME_MAP.values():
            assert isinstance(value, BiometryMeasurement)

        for value in VIEWPOINT_TEXT_NAME_MAP.values():
            assert isinstance(value, BiometryMeasurement)

        for value in VIEWPOINT_HL7_NAME_MAP.values():
            assert isinstance(value, BiometryMeasurement)
