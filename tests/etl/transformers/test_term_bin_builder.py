"""
Tests for TermBinBuilder transformer.

Following TDD methodology for transforming BiometryCollection to TermBins.
"""

import pytest
from unittest.mock import patch
from pathlib import Path

from prenatalppkt.etl.models.biometry import Biometry, BiometryCollection
from prenatalppkt.etl.transformers.term_bin_builder import TermBinBuilder
from prenatalppkt.measurements.term_bin import TermBin
from prenatalppkt.measurements.percentile_range import PercentileRange
from prenatalppkt.gestational_age import GestationalAge


class TestTermBinBuilder:
    """Test suite for TermBinBuilder."""

    @pytest.fixture
    def mock_mappings(self):
        """Mock HPO mappings for testing."""
        # Create mock TermBins for HC (Head Circumference)
        # Using actual percentile ranges from PercentileRange static methods
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
            TermBin(
                range=PercentileRange.above_97p(),
                hpo_id="HP:0000256",
                hpo_label="Macrocephaly",
                normal=False,
                description="Above 97th percentile",
            ),
        ]

        return {"head_circumference": hc_bins}

    @pytest.fixture
    def builder_with_mocks(self, mock_mappings):
        """Create TermBinBuilder with mocked mappings."""
        # Patch the BiometryMappingLoader.load method
        with patch(
            "prenatalppkt.etl.transformers.term_bin_builder.BiometryMappingLoader.load"
        ) as mock_load:
            mock_load.return_value = mock_mappings
            builder = TermBinBuilder()
            return builder

    def test_build_single_biometry(self, builder_with_mocks):
        """Test building TermBin from single biometry."""
        biometry = Biometry(
            name="HC",
            value_mm=180.0,
            percentile=2.0,  # Below 3rd percentile
            gestational_age=GestationalAge(weeks=25, days=0),
            method="Hadlock",
            fetus_number=1,
        )

        collection = BiometryCollection(measurements=[biometry], fetus_number=1)

        term_bins = builder_with_mocks.build(collection)

        assert len(term_bins) == 1
        assert term_bins[0].hpo_id == "HP:0000252"
        assert term_bins[0].hpo_label == "Microcephaly"
        assert term_bins[0].normal is False
        assert "180.0 mm" in term_bins[0].description
        assert "(2.0%)" in term_bins[0].description

    def test_build_multiple_biometries(self, builder_with_mocks):
        """Test building TermBins from multiple biometries."""
        measurements = [
            Biometry(
                name="HC",
                value_mm=180.0,
                percentile=2.0,
                gestational_age=GestationalAge(weeks=25, days=0),
                method="Hadlock",
            ),
            Biometry(
                name="HC",
                value_mm=200.0,
                percentile=30.0,
                gestational_age=GestationalAge(weeks=25, days=0),
                method="Hadlock",
            ),
        ]

        collection = BiometryCollection(measurements=measurements)
        term_bins = builder_with_mocks.build(collection)

        assert len(term_bins) == 2
        assert term_bins[0].hpo_id == "HP:0000252"  # Microcephaly
        assert term_bins[1].hpo_id == "HP:0000240"  # Abnormality of skull size

    def test_biometry_without_percentile_skipped(self, builder_with_mocks):
        """Test that biometries without percentiles are skipped."""
        biometry = Biometry(
            name="HC",
            value_mm=200.0,
            percentile=None,  # No percentile
            gestational_age=GestationalAge(weeks=25, days=0),
        )

        collection = BiometryCollection(measurements=[biometry])
        term_bins = builder_with_mocks.build(collection)

        assert len(term_bins) == 0

    def test_unmapped_measurement_type_skipped(self, builder_with_mocks):
        """Test that unmapped measurement types are skipped."""
        biometry = Biometry(
            name="BPD",  # Not in mock mappings
            value_mm=60.0,
            percentile=50.0,
            gestational_age=GestationalAge(weeks=25, days=0),
        )

        collection = BiometryCollection(measurements=[biometry])
        term_bins = builder_with_mocks.build(collection)

        assert len(term_bins) == 0

    def test_percentile_outside_bins_skipped(self, builder_with_mocks):
        """Test that percentiles not matching any bin are skipped."""
        biometry = Biometry(
            name="HC",
            value_mm=200.0,
            percentile=5.0,  # Between 3-10, not in our mock bins
            gestational_age=GestationalAge(weeks=25, days=0),
        )

        collection = BiometryCollection(measurements=[biometry])
        term_bins = builder_with_mocks.build(collection)

        # Should skip since 5% bin (between_5p_10p) is not in our mock mappings
        assert len(term_bins) == 0

    def test_description_formatting(self, builder_with_mocks):
        """Test description string formatting."""
        biometry = Biometry(
            name="HC",
            value_mm=233.7,
            percentile=36.0,
            gestational_age=GestationalAge(weeks=25, days=1),
            method="Hadlock",
            fetus_number=1,
        )

        term_bin = builder_with_mocks._build_single(biometry)

        assert term_bin is not None
        assert "HC: 233.7 mm" in term_bin.description
        assert "(36.0%)" in term_bin.description
        assert "at 25w1d" in term_bin.description
        assert "(Hadlock)" in term_bin.description
        assert "[Fetus 1]" in term_bin.description

    def test_description_minimal_fields(self, builder_with_mocks):
        """Test description with minimal fields."""
        biometry = Biometry(
            name="HC",
            value_mm=200.0,
            percentile=30.0,
            gestational_age=None,
            method=None,
            fetus_number=None,
        )

        term_bin = builder_with_mocks._build_single(biometry)

        assert term_bin is not None
        # Should only include required fields
        assert "HC: 200.0 mm (30.0%)" in term_bin.description
        assert "at" not in term_bin.description
        assert "Fetus" not in term_bin.description

    def test_normalize_measurement_type(self, builder_with_mocks):
        """Test measurement name normalization."""
        assert (
            builder_with_mocks._normalize_measurement_type("HC") == "head_circumference"
        )
        assert (
            builder_with_mocks._normalize_measurement_type("BPD")
            == "biparietal_diameter"
        )
        assert (
            builder_with_mocks._normalize_measurement_type("Nuchal Fold")
            == "nuchal_fold"
        )
        assert builder_with_mocks._normalize_measurement_type("Femur") == "femur_length"

    def test_empty_collection_returns_empty_list(self, builder_with_mocks):
        """Test that empty collection returns empty list."""
        collection = BiometryCollection(measurements=[])
        term_bins = builder_with_mocks.build(collection)

        assert len(term_bins) == 0

    def test_error_handling_continues_processing(self, builder_with_mocks):
        """Test that errors on one biometry don't stop processing others."""
        measurements = [
            Biometry(
                name="HC",
                value_mm=180.0,
                percentile=2.0,
                gestational_age=GestationalAge(weeks=25, days=0),
            ),
            Biometry(
                name="INVALID",  # Will cause error
                value_mm=100.0,
                percentile=50.0,
            ),
            Biometry(
                name="HC",
                value_mm=200.0,
                percentile=30.0,
                gestational_age=GestationalAge(weeks=25, days=0),
            ),
        ]

        collection = BiometryCollection(measurements=measurements)
        term_bins = builder_with_mocks.build(collection)

        # Should process valid ones despite error on invalid
        assert len(term_bins) == 2


class TestTermBinBuilderIntegration:
    """Integration tests with real mapping files."""

    @pytest.mark.skipif(
        not Path("data/mappings/biometry_hpo_mappings.yaml").exists(),
        reason="Mapping file not found",
    )
    def test_load_real_mappings(self):
        """Test loading real HPO mappings from YAML."""
        builder = TermBinBuilder()

        # Should have mappings for all 8 target measurements
        assert "head_circumference" in builder._mappings
        assert "biparietal_diameter" in builder._mappings
        assert "abdominal_circumference" in builder._mappings
        assert "femur_length" in builder._mappings

    @pytest.mark.skipif(
        not Path("data/mappings/biometry_hpo_mappings.yaml").exists(),
        reason="Mapping file not found",
    )
    def test_build_with_real_mappings(self):
        """Test building TermBins with real mappings."""
        builder = TermBinBuilder()

        # Test with microcephaly case (low HC)
        biometry = Biometry(
            name="HC",
            value_mm=180.0,
            percentile=2.0,
            gestational_age=GestationalAge(weeks=25, days=0),
            method="Hadlock",
        )

        collection = BiometryCollection(measurements=[biometry])
        term_bins = builder.build(collection)

        assert len(term_bins) == 1
        assert term_bins[0].normal is False
        assert "microcephaly" in term_bins[0].hpo_label.lower()
