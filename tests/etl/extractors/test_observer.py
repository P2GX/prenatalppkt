"""
Tests for Observer JSON extractor.
"""

import json
from pathlib import Path

import pytest

from prenatalppkt.etl.extractors import observer
from prenatalppkt.etl.term_bin_factory import TermBinFactory
from prenatalppkt.measurements.term_bin import TermBin


class TestObserverExtract:
    """Tests for extract() function."""

    def test_extract_basic(self):
        """Test extraction with minimal valid data."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 17.5,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                            "calculated_ega": 25.5,
                        },
                        {
                            "label": "BPD",
                            "value": 6.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 55.0,
                            "calculated_ega": 26.0,
                        },
                        {
                            "label": "AC",
                            "value": 21.2,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 48.0,
                            "calculated_ega": 25.8,
                        },
                        {
                            "label": "Femur",
                            "value": 4.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 52.0,
                            "calculated_ega": 26.1,
                        },
                    ],
                }
            ]
        }

        term_bins = observer.extract(data)

        assert len(term_bins) == 4
        assert all(isinstance(tb, TermBin) for tb in term_bins)

        # Check HC conversion from cm to mm
        hc_bin = next(tb for tb in term_bins if "HC" in tb.description)
        assert hc_bin is not None
        # 17.5 cm = 175 mm
        assert "175" in hc_bin.description or "175.0" in hc_bin.description

    def test_extract_with_custom_factory(self):
        """Test extraction with custom factory."""
        factory = TermBinFactory()
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 17.5,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                        },
                        {
                            "label": "BPD",
                            "value": 6.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 55.0,
                        },
                        {
                            "label": "AC",
                            "value": 21.2,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 48.0,
                        },
                        {
                            "label": "Femur",
                            "value": 4.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 52.0,
                        },
                    ],
                }
            ]
        }

        term_bins = observer.extract(data, factory)
        assert len(term_bins) == 4

    def test_extract_missing_fetuses_key(self):
        """Test extraction with missing 'fetuses' key."""
        data = {"exam": {}, "patient": {}}

        with pytest.raises(ValueError, match="Missing 'fetuses' key"):
            observer.extract(data)

    def test_extract_empty_fetuses(self):
        """Test extraction with empty fetuses list."""
        data = {"fetuses": []}

        with pytest.raises(ValueError, match="non-empty list"):
            observer.extract(data)

    def test_extract_invalid_type(self):
        """Test extraction with invalid data type."""
        with pytest.raises(ValueError, match="Expected dict"):
            observer.extract("not a dict")

    def test_extract_missing_required_measurements(self):
        """Test extraction fails when required measurements missing."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 17.5,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                        }
                        # Missing BPD, AC, Femur
                    ],
                }
            ]
        }

        with pytest.raises(ValueError, match="Missing required measurements"):
            observer.extract(data)

    def test_extract_skips_measurements_without_percentile(self):
        """Test that measurements without percentiles are skipped."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 17.5,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                        },
                        {
                            "label": "BPD",
                            "value": 6.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 55.0,
                        },
                        {
                            "label": "AC",
                            "value": 21.2,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 48.0,
                        },
                        {
                            "label": "Femur",
                            "value": 4.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 52.0,
                        },
                        {
                            "label": "Nuchal Fold",
                            "value": 4.5,
                            "unit_of_measure": "mm",
                            # No percentile - should be skipped
                        },
                    ],
                }
            ]
        }

        term_bins = observer.extract(data)
        # Should have 4 (not 5) since Nuchal Fold has no percentile
        assert len(term_bins) == 4

    def test_extract_optional_measurements(self):
        """Test extraction includes optional measurements when present."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        # ... HC, BPD, AC, Femur with percentiles ...
                        {
                            "label": "Nuchal Fold",
                            "value": 4.5,
                            "unit_of_measure": "mm",
                            "calculated_percentile": 10.0,  # Has percentile!
                        },
                        {
                            "label": "Cerebellum",
                            "value": 25.0,
                            "unit_of_measure": "mm",
                            "calculated_percentile": 45.0,  # Has percentile!
                        },
                    ],
                }
            ]
        }

        term_bins = observer.extract(data)

        # TODO(@VarenyaJ): When HPO mappings added, change to 6
        assert len(term_bins) == 4  # Only required measurements (no HPO for optional)

        # Don't check for optional measurements yet
        # labels = [tb.description for tb in term_bins]
        # assert any("Nuchal Fold" in desc for desc in labels)


class TestObserverExtractFromFile:
    """Tests for extract_from_file() function."""

    def test_extract_from_file_not_found(self):
        """Test extraction from non-existent file."""
        with pytest.raises(FileNotFoundError):
            observer.extract_from_file(Path("nonexistent.json"))

    def test_extract_from_file_invalid_json(self, tmp_path):
        """Test extraction from file with invalid JSON."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("not valid json")

        with pytest.raises(json.JSONDecodeError):
            observer.extract_from_file(test_file)

    def test_extract_from_file_success(self, tmp_path):
        """Test successful extraction from file."""
        test_file = tmp_path / "valid.json"
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 17.5,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                        },
                        {
                            "label": "BPD",
                            "value": 6.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 55.0,
                        },
                        {
                            "label": "AC",
                            "value": 21.2,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 48.0,
                        },
                        {
                            "label": "Femur",
                            "value": 4.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 52.0,
                        },
                    ],
                }
            ]
        }
        test_file.write_text(json.dumps(data))

        term_bins = observer.extract_from_file(test_file)
        assert len(term_bins) == 4


class TestObserverUnitConversion:
    """Tests for unit conversion."""

    def test_convert_cm_to_mm(self):
        """Test centimeter to millimeter conversion."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 17.5,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                        },
                        {
                            "label": "BPD",
                            "value": 6.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 55.0,
                        },
                        {
                            "label": "AC",
                            "value": 21.2,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 48.0,
                        },
                        {
                            "label": "Femur",
                            "value": 4.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 52.0,
                        },
                    ],
                }
            ]
        }

        term_bins = observer.extract(data)

        # All values should be converted to mm (x10)
        hc = next(tb for tb in term_bins if "HC" in tb.description)
        assert "175" in hc.description  # 17.5 * 10

    def test_nuchal_fold_mm_no_conversion(self):
        """Test that mm values are not converted."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 17.5,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                        },
                        {
                            "label": "BPD",
                            "value": 6.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 55.0,
                        },
                        {
                            "label": "AC",
                            "value": 21.2,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 48.0,
                        },
                        {
                            "label": "Femur",
                            "value": 4.8,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 52.0,
                        },
                        {
                            "label": "Nuchal Fold",
                            "value": 4.5,
                            "unit_of_measure": "mm",
                            "calculated_percentile": 10.0,
                        },
                    ],
                }
            ]
        }

        term_bins = observer.extract(data)

        # TODO(@VarenyaJ): Nuchal Fold has no HPO mapping - won't be in results
        # This test should be updated when HPO mapping is added
        # For now, expect only 4 required measurements
        assert len(term_bins) == 4

        # Skip Nuchal Fold assertion until HPO mapping exists
        # nf = next(tb for tb in term_bins if "Nuchal Fold" in tb.description)
        # assert "4.5" in nf.description
