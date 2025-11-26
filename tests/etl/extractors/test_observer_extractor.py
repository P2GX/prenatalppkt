"""
Tests for ObserverExtractor.

Following TDD methodology:
1. Write failing test
2. Implement minimal code to pass
3. Refactor
4. Repeat
"""

import pytest
from prenatalppkt.etl.extractors.observer import ObserverExtractor
from prenatalppkt.etl.models.biometry import BiometryCollection
from prenatalppkt.gestational_age import GestationalAge


class TestObserverExtractor:
    """Test suite for Observer JSON extraction."""

    @pytest.fixture
    def minimal_json(self):
        """Minimal valid Observer JSON for testing."""
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
    def full_biometry_json(self):
        """Complete Observer JSON with all target biometries."""
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
                            "calculated_ega": 27.3,
                        },
                        {
                            "label": "Femur",
                            "value": 5.01,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 46.8,
                            "calculated_ega": 27.1,
                        },
                        {
                            "label": "Nuchal Fold",
                            "value": 1.0,
                            "unit_of_measure": "mm",
                            "calculated_percentile": 0.0,
                            "calculated_ega": 27.1,
                        },
                        {
                            "label": "Cerebellum",
                            "value": 3.0,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 0.0,
                            "calculated_ega": 27.4,
                        },
                        {
                            "label": "OFD",
                            "value": 8.5,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 45.0,
                            "calculated_ega": 27.0,
                        },
                        {
                            "label": "Humerus",
                            "value": 4.2,
                            "unit_of_measure": "cm",
                            "calculated_percentile": 50.0,
                            "calculated_ega": 26.5,
                        },
                    ],
                }
            ]
        }

    def test_extract_returns_biometry_collection(self, minimal_json):
        """Test that extract returns BiometryCollection object."""
        extractor = ObserverExtractor()
        result = extractor.extract(minimal_json)

        assert isinstance(result, BiometryCollection)

    def test_extract_single_hc_measurement(self, minimal_json):
        """Test extraction of single HC measurement."""
        extractor = ObserverExtractor()
        collection = extractor.extract(minimal_json)

        assert collection.count == 1

        hc = collection.get("HC")
        assert hc is not None
        assert hc.name == "HC"
        assert hc.value_mm == 250.0  # 25.0 cm -> 250.0 mm
        assert hc.percentile == 42.5
        assert isinstance(hc.gestational_age, GestationalAge)
        assert hc.gestational_age.weeks == 27
        assert hc.gestational_age.days == 0

        assert hc.fetus_number == 1

    def test_extract_all_eight_biometries(self, full_biometry_json):
        """Test extraction of all 8 target biometries."""
        extractor = ObserverExtractor()
        collection = extractor.extract(full_biometry_json)

        assert collection.count == 8

        expected_names = [
            "HC",
            "BPD",
            "AC",
            "Femur",
            "Nuchal Fold",
            "Cerebellum",
            "OFD",
            "Humerus",
        ]

        for name in expected_names:
            measurement = collection.get(name)
            assert measurement is not None, f"Missing {name}"
            assert measurement.value_mm > 0

    def test_unit_conversion_cm_to_mm(self, minimal_json):
        """Test that cm values are correctly converted to mm."""
        extractor = ObserverExtractor()
        collection = extractor.extract(minimal_json)

        hc = collection.get("HC")
        # Original: 25.0 cm, Expected: 250.0 mm
        assert hc.value_mm == pytest.approx(250.0)

    def test_unit_conversion_mm_unchanged(self):
        """Test that mm values are not converted."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "Nuchal Fold",
                            "value": 1.0,
                            "unit_of_measure": "mm",
                            "calculated_percentile": 0.0,
                        }
                    ],
                }
            ]
        }

        extractor = ObserverExtractor()
        collection = extractor.extract(data)

        nuchal = collection.get("Nuchal Fold")
        # Original: 1.0 mm, Expected: 1.0 mm
        assert nuchal.value_mm == pytest.approx(1.0)

    def test_gestational_age_formatting(self):
        """Test gestational age formatting from EGA."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "value": 25.0,
                            "unit_of_measure": "cm",
                            "calculated_ega": 27.6,  # 27 weeks + 4.2 days
                        }
                    ],
                }
            ]
        }

        extractor = ObserverExtractor()
        collection = extractor.extract(data)

        hc = collection.get("HC")
        # 27.6 weeks -> 27 weeks + 4 days
        assert isinstance(hc.gestational_age, GestationalAge)
        assert hc.gestational_age.weeks == 27
        assert hc.gestational_age.days == 4

    def test_fetus_number_extraction(self, full_biometry_json):
        """Test that fetus number is correctly extracted."""
        extractor = ObserverExtractor()
        collection = extractor.extract(full_biometry_json)

        assert collection.fetus_number == 1

        # All measurements should have same fetus number
        for measurement in collection.measurements:
            assert measurement.fetus_number == 1

    def test_missing_fetuses_key_raises_error(self):
        """Test that missing 'fetuses' key raises ValueError."""
        extractor = ObserverExtractor()

        with pytest.raises(ValueError, match="Missing 'fetuses' key"):
            extractor.extract({"patient": "test"})

    def test_empty_fetuses_list_raises_error(self):
        """Test that empty fetuses list raises ValueError."""
        extractor = ObserverExtractor()

        with pytest.raises(ValueError, match="must be non-empty list"):
            extractor.extract({"fetuses": []})

    def test_missing_measurements_returns_empty_collection(self):
        """Test that missing measurements key returns empty collection."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1}
                    # No measurements key
                }
            ]
        }

        extractor = ObserverExtractor()
        collection = extractor.extract(data)

        assert collection.count == 0

    def test_non_target_measurements_ignored(self):
        """Test that non-target measurements are ignored."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {"label": "HC", "value": 25.0, "unit_of_measure": "cm"},
                        {
                            "label": "Unknown Measurement",
                            "value": 10.0,
                            "unit_of_measure": "cm",
                        },
                    ],
                }
            ]
        }

        extractor = ObserverExtractor()
        collection = extractor.extract(data)

        assert collection.count == 1
        assert collection.get("HC") is not None
        assert collection.get("Unknown Measurement") is None

    def test_measurement_without_value_skipped(self):
        """Test that measurements without value are skipped."""
        data = {
            "fetuses": [
                {
                    "fetus": {"fetus_number": 1},
                    "measurements": [
                        {
                            "label": "HC",
                            "unit_of_measure": "cm",
                            # No value
                        }
                    ],
                }
            ]
        }

        extractor = ObserverExtractor()
        collection = extractor.extract(data)

        assert collection.count == 0

    def test_percentile_none_when_missing(self):
        """Test that percentile is None when not provided."""
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

        extractor = ObserverExtractor()
        collection = extractor.extract(data)

        hc = collection.get("HC")
        assert hc.percentile is None
