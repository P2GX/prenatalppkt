"""
Tests for Observer JSON extractor.

Tests extraction of biometry measurements and conversion to TermBins.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from prenatalppkt.etl.extractors import observer
from prenatalppkt.etl.term_bin_factory import TermBinFactory
from prenatalppkt.measurements.term_bin import TermBin


class TestObserverExtractor:
    """Test suite for Observer JSON extraction."""

    @pytest.fixture
    def mock_factory(self):
        """Mock TermBinFactory for testing."""
        factory = Mock(spec=TermBinFactory)

        def create_mock_term_bin(name, **kwargs):
            """Create mock TermBin with predictable properties."""
            return Mock(
                spec=TermBin,
                description=f"{name}: {kwargs['value_mm']} mm ({kwargs['percentile']}%)",
                hpo_id=f"HP:TEST_{name}",
                hpo_label=f"Test {name}",
                normal=True,
            )

        factory.create_term_bin.side_effect = create_mock_term_bin
        return factory

    @pytest.fixture
    def minimal_json(self):
        """Minimal valid Observer JSON."""
        return {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 25.0,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 42.5,
                            "calculated_ega": 27.1,
                        }
                    ],
                }
            ]
        }

    @pytest.fixture
    def full_json(self):
        """Complete Observer JSON with all required biometries."""
        return {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 25.0,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 42.5,
                            "calculated_ega": 27.1,
                        },
                        {
                            "label": "BPD",
                            "value": 6.68,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 51.2,
                            "calculated_ega": 26.9,
                        },
                        {
                            "label": "AC",
                            "value": 22.62,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 55.6,
                            "calculated_ega": 26.9,
                        },
                        {
                            "label": "Femur",
                            "value": 5.01,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 46.8,
                            "calculated_ega": 27.1,
                        },
                    ],
                }
            ]
        }

    def test_extract_returns_list_of_term_bins(self, minimal_json, mock_factory):
        """Test that extract returns list of TermBin objects."""
        with patch(
            "prenatalppkt.etl.extractors.observer.validate_required_measurements"
        ):
            result = observer.extract(minimal_json, mock_factory)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Mock)  # Mock TermBin

    def test_extract_validates_required_measurements(self, full_json, mock_factory):
        """Test that validation is called."""
        with patch(
            "prenatalppkt.etl.extractors.observer.validate_required_measurements"
        ) as mock_validate:
            observer.extract(full_json, mock_factory)
            mock_validate.assert_called_once()

    def test_unit_conversion_cm_to_mm(self, minimal_json, mock_factory):
        """Test that cm values are converted to mm."""
        with patch(
            "prenatalppkt.etl.extractors.observer.validate_required_measurements"
        ):
            observer.extract(minimal_json, mock_factory)

        # Check factory was called with converted value
        call_kwargs = mock_factory.create_term_bin.call_args[1]
        assert call_kwargs["value_mm"] == 250.0  # 25.0 cm -> 250.0 mm

    def test_missing_fetuses_key_raises_error(self, mock_factory):
        """Test that missing 'fetuses' key raises ValueError."""
        with pytest.raises(ValueError, match="Missing 'fetuses' key"):
            observer.extract({"patient": "test"}, mock_factory)

    def test_empty_fetuses_list_raises_error(self, mock_factory):
        """Test that empty fetuses list raises ValueError."""
        with pytest.raises(ValueError, match="must be non-empty list"):
            observer.extract({"fetuses": []}, mock_factory)

    def test_measurement_without_percentile_skipped(self, mock_factory):
        """Test that measurements without percentile are skipped."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 25.0,
                            "unit_of_measure": "cm",
                            # No calculated_percentile
                        }
                    ],
                }
            ]
        }

        with patch(
            "prenatalppkt.etl.extractors.observer.validate_required_measurements"
        ):
            result = observer.extract(data, mock_factory)

        assert len(result) == 0

    def test_non_target_measurement_ignored(self, mock_factory):
        """Test that non-target measurements are ignored."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "Unknown",
                            "value": 10.0,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                        }
                    ],
                }
            ]
        }

        with patch(
            "prenatalppkt.etl.extractors.observer.validate_required_measurements"
        ):
            result = observer.extract(data, mock_factory)

        assert len(result) == 0

    def test_extract_from_file(self, tmp_path, minimal_json, mock_factory):
        """Test extract_from_file function."""
        # Write test file
        test_file = tmp_path / "test.json"
        import json

        test_file.write_text(json.dumps(minimal_json))

        with patch(
            "prenatalppkt.etl.extractors.observer.validate_required_measurements"
        ):
            result = observer.extract_from_file(test_file, mock_factory)

        assert isinstance(result, list)
        assert len(result) == 1


class TestObserverIntegration:
    """Integration tests with real Observer JSON file."""

    @pytest.mark.skipif(
        not Path("tests/data/Apple_Sally_pretty.json").exists(),
        reason="Test data file not found",
    )
    def test_extract_from_real_file(self):
        """Test extraction from real Observer JSON file."""
        filepath = Path("tests/data/Apple_Sally_pretty.json")

        # This will use real factory and mappings
        term_bins = observer.extract_from_file(filepath)

        # Should have extracted required measurements
        assert len(term_bins) >= 4  # At least HC, BPD, AC, Femur

        # All should be TermBin objects
        for tb in term_bins:
            assert isinstance(tb, TermBin)
            assert tb.hpo_id.startswith("HP:")
            assert tb.description
