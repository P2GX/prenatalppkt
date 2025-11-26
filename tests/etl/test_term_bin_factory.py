"""
Tests for TermBinFactory.

Tests the factory's ability to create TermBin objects from raw measurements
using existing MeasurementEvaluation infrastructure.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from prenatalppkt.etl.term_bin_factory import (
    TermBinFactory,
    validate_required_measurements,
)
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.term_bin import TermBin
from prenatalppkt.measurements.percentile_range import PercentileRange


class TestTermBinFactory:
    """Test suite for TermBinFactory."""

    @pytest.fixture
    def mock_mappings(self):
        """Mock HPO mappings for testing."""
        # Create mock TermBins for HC
        hc_bins = [
            TermBin(
                range=PercentileRange.below_3p(),
                hpo_id="HP:0000252",
                hpo_label="Microcephaly",
                normal=False,
                description="Below 3rd percentile",
            ),
            TermBin(
                range=PercentileRange.between_10p_50p(),
                hpo_id="HP:0000240",
                hpo_label="Abnormality of skull size",
                normal=True,
                description="10th-50th percentile",
            ),
        ]
        return {"head_circumference": hc_bins}

    @pytest.fixture
    def factory(self, mock_mappings):
        """Create factory with mocked mappings."""
        with patch(
            "prenatalppkt.etl.term_bin_factory.BiometryMappingLoader.load"
        ) as mock_load:
            mock_load.return_value = mock_mappings
            return TermBinFactory()

    def test_create_term_bin_basic(self, factory):
        """Test creating TermBin from basic measurement."""
        term_bin = factory.create_term_bin(
            name="HC",
            value_mm=180.0,
            percentile=2.0,
            gestational_age=GestationalAge(weeks=27, days=1),
        )

        assert term_bin is not None
        assert term_bin.hpo_id == "HP:0000252"
        assert term_bin.hpo_label == "Microcephaly"
        assert term_bin.normal is False
        assert "180.0 mm" in term_bin.description
        assert "(2.0%)" in term_bin.description

    def test_create_term_bin_with_all_fields(self, factory):
        """Test creating TermBin with all optional fields."""
        term_bin = factory.create_term_bin(
            name="HC",
            value_mm=233.7,
            percentile=36.0,
            gestational_age=GestationalAge(weeks=25, days=1),
            method="Hadlock",
            fetus_number=1,
        )

        assert term_bin is not None
        assert "25w1d" in term_bin.description
        assert "(Hadlock)" in term_bin.description
        assert "[Fetus 1]" in term_bin.description

    def test_create_term_bin_invalid_percentile(self, factory):
        """Test that invalid percentile raises error."""
        with pytest.raises(ValueError, match="Percentile must be 0-100"):
            factory.create_term_bin(name="HC", value_mm=200.0, percentile=150.0)

    def test_create_term_bin_no_mapping(self, factory):
        """Test that unmapped measurement returns None."""
        term_bin = factory.create_term_bin(
            name="BPD",  # Not in mock mappings
            value_mm=60.0,
            percentile=50.0,
        )

        assert term_bin is None

    def test_create_term_bin_percentile_no_bin(self, factory):
        """Test percentile that doesn't match any bin."""
        term_bin = factory.create_term_bin(
            name="HC",
            value_mm=200.0,
            percentile=5.0,  # Between 3-10, not in mock bins
        )

        assert term_bin is None

    def test_normalize_measurement_type(self, factory):
        """Test measurement name normalization."""
        assert factory._normalize_measurement_type("HC") == "head_circumference"
        assert factory._normalize_measurement_type("BPD") == "biparietal_diameter"
        assert factory._normalize_measurement_type("Nuchal Fold") == "nuchal_fold"


class TestValidateRequiredMeasurements:
    """Test validation of required measurements."""

    def test_all_required_present(self):
        """Test validation passes with all required measurements."""
        term_bins = [
            MagicMock(description="HC: 250.0 mm (42%)"),
            MagicMock(description="BPD: 63.2 mm (36%)"),
            MagicMock(description="AC: 226.2 mm (55%)"),
            MagicMock(description="Femur: 50.1 mm (46%)"),
        ]

        # Should not raise
        validate_required_measurements(term_bins)

    def test_missing_required_measurement(self):
        """Test validation fails with missing required measurement."""
        term_bins = [
            MagicMock(description="HC: 250.0 mm (42%)"),
            MagicMock(description="BPD: 63.2 mm (36%)"),
            # Missing AC and Femur
        ]

        with pytest.raises(ValueError, match="Missing required biometry measurements"):
            validate_required_measurements(term_bins)

    def test_error_message_lists_missing(self):
        """Test error message lists missing measurements."""
        term_bins = [MagicMock(description="HC: 250.0 mm (42%)")]

        with pytest.raises(ValueError) as exc_info:
            validate_required_measurements(term_bins)

        error_msg = str(exc_info.value)
        assert "AC" in error_msg
        assert "BPD" in error_msg
        assert "Femur" in error_msg

    def test_optional_measurements_not_required(self):
        """Test that optional measurements don't affect validation."""
        term_bins = [
            MagicMock(description="HC: 250.0 mm (42%)"),
            MagicMock(description="BPD: 63.2 mm (36%)"),
            MagicMock(description="AC: 226.2 mm (55%)"),
            MagicMock(description="Femur: 50.1 mm (46%)"),
            MagicMock(description="Nuchal Fold: 4.5 mm (10%)"),  # Optional
        ]

        # Should not raise
        validate_required_measurements(term_bins)


class TestTermBinFactoryIntegration:
    """Integration tests with real mappings."""

    @pytest.mark.skipif(
        not (
            Path(__file__).parent.parent.parent
            / "data"
            / "mappings"
            / "biometry_hpo_mappings.yaml"
        ).exists(),
        reason="Mapping file not found",
    )
    def test_create_with_real_mappings(self):
        """Test creating TermBins with real mapping file."""

        factory = TermBinFactory()

        # Test microcephaly case
        term_bin = factory.create_term_bin(name="HC", value_mm=180.0, percentile=2.0)

        assert term_bin is not None
        assert term_bin.normal is False
        assert "microcephaly" in term_bin.hpo_label.lower()
