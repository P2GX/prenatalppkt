"""
tests/test_measurements_parser.py

Unit tests for MeasurementsParser and MeasurementsData
"""

import pytest
from prenatalppkt.parser.observer.measurements_parser import MeasurementsParser
from prenatalppkt.dto.measurements_data import MeasurementsData, Measurement


class TestMeasurement:
    """Tests for the Measurement dataclass."""

    def test_measurement_creation(self):
        """Test creating a basic Measurement object."""
        m = Measurement(
            label="AC",
            value=22.62,
            unit_of_measure="cm",
            calculated_percentile=55.6,
            calculated_z_score=0.14,
            calculated_ega=26.9,
            fetus_number=1,
        )

        assert m.label == "AC"
        assert m.value == 22.62
        assert m.unit_of_measure == "cm"
        assert m.calculated_percentile == 55.6
        assert m.calculated_z_score == 0.14
        assert m.calculated_ega == 26.9
        assert m.fetus_number == 1


class TestMeasurementsData:
    """Tests for the MeasurementsData class."""

    @pytest.fixture
    def sample_measurements(self):
        """Create sample measurements for testing."""
        return [
            Measurement("AC", 22.62, "cm", 55.6, 0.14, 26.9, 1),
            Measurement("BPD", 6.68, "cm", 51.2, 0.03, 26.9, 1),
            Measurement("HC", 25.0, "cm", 42.5, -0.19, 26.9, 1),
            Measurement("Femur", 5.01, "cm", 46.8, -0.08, 27.1, 1),
            Measurement("Nuchal Fold", 1.0, "cm", 0.0, 0.0, 0.0, 1),
            Measurement("Cerebellum", 3.0, "cm", 0.0, 0.0, 27.4, 1),
        ]

    def test_measurements_data_creation(self, sample_measurements):
        """Test creating MeasurementsData object."""
        data = MeasurementsData(fetus_number=1, measurements=sample_measurements)

        assert data.fetus_number == 1
        assert data.measurement_count == 6
        assert len(data.measurements) == 6

    def test_get_measurement_by_label(self, sample_measurements):
        """Test retrieving measurements by label."""
        data = MeasurementsData(fetus_number=1, measurements=sample_measurements)

        # Test exact match
        ac = data.get_measurement_by_label("AC")
        assert ac is not None
        assert ac.label == "AC"
        assert ac.value == 22.62

        # Test case-insensitive
        bpd = data.get_measurement_by_label("bpd")
        assert bpd is not None
        assert bpd.label == "BPD"
        assert bpd.value == 6.68

        # Test with spaces
        nuchal = data.get_measurement_by_label("nuchal fold")
        assert nuchal is not None
        assert nuchal.label == "Nuchal Fold"
        assert nuchal.value == 1.0

        # Test non-existent
        missing = data.get_measurement_by_label("OFD")
        assert missing is None

    def test_measurement_count(self, sample_measurements):
        """Test measurement count property."""
        data = MeasurementsData(fetus_number=1, measurements=sample_measurements)
        assert data.measurement_count == 6

        # Test with empty list
        empty_data = MeasurementsData(fetus_number=1, measurements=[])
        assert empty_data.measurement_count == 0

    def test_all_major_measurements_present(self, sample_measurements):
        """Test that all major biometric measurements are present."""
        data = MeasurementsData(fetus_number=1, measurements=sample_measurements)

        expected_measurements = [
            "AC",
            "BPD",
            "HC",
            "Femur",
            "Nuchal Fold",
            "Cerebellum",
        ]

        for label in expected_measurements:
            m = data.get_measurement_by_label(label)
            assert m is not None, f"Missing measurement: {label}"
            assert m.value > 0, f"Invalid value for {label}: {m.value}"


class TestMeasurementsParser:
    """Tests for the MeasurementsParser class."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return MeasurementsParser()

    @pytest.fixture
    def sample_fetus_data(self):
        """Sample fetus data matching the JSON structure."""
        return {
            "fetus": {"fetus_number": 1},
            "measurements": [
                {
                    "label": "AC",
                    "value": 22.62,
                    "unit_of_measure": "cm",
                    "calculated_percentile": 55.6,
                    "calculated_z_score": 0,
                    "calculated_ega": 26.9,
                    "fetus_number": 1,
                },
                {
                    "label": "BPD",
                    "value": 6.68,
                    "unit_of_measure": "cm",
                    "calculated_percentile": 51.2,
                    "calculated_z_score": 0,
                    "calculated_ega": 26.9,
                    "fetus_number": 1,
                },
                {
                    "label": "HC",
                    "value": 25.0,
                    "unit_of_measure": "cm",
                    "calculated_percentile": 42.5,
                    "calculated_z_score": 0,
                    "calculated_ega": 26.9,
                    "fetus_number": 1,
                },
                {
                    "label": "Femur",
                    "value": 5.01,
                    "unit_of_measure": "cm",
                    "calculated_percentile": 46.8,
                    "calculated_z_score": 0,
                    "calculated_ega": 27.1,
                    "fetus_number": 1,
                },
                {
                    "label": "Nuchal Fold",
                    "value": 1.0,
                    "unit_of_measure": "cm",
                    "calculated_percentile": 0,
                    "calculated_z_score": 0,
                    "calculated_ega": 0,
                    "fetus_number": 1,
                },
                {
                    "label": "Cerebellum",
                    "value": 3.0,
                    "unit_of_measure": "cm",
                    "calculated_percentile": 0,
                    "calculated_z_score": 0,
                    "calculated_ega": 27.4,
                    "fetus_number": 1,
                },
            ],
        }

    def test_parse_basic(self, parser, sample_fetus_data):
        """Test basic parsing of measurements."""
        result = parser.parse(sample_fetus_data)

        assert isinstance(result, MeasurementsData)
        assert result.fetus_number == 1
        assert result.measurement_count == 6

    def test_parse_all_measurements(self, parser, sample_fetus_data):
        """Test that all measurements are parsed correctly."""
        result = parser.parse(sample_fetus_data)

        # Verify each measurement
        expected = [
            ("AC", 22.62, 55.6),
            ("BPD", 6.68, 51.2),
            ("HC", 25.0, 42.5),
            ("Femur", 5.01, 46.8),
            ("Nuchal Fold", 1.0, 0.0),
            ("Cerebellum", 3.0, 0.0),
        ]

        for label, value, percentile in expected:
            m = result.get_measurement_by_label(label)
            assert m is not None, f"Measurement {label} not found"
            assert m.value == value, f"Wrong value for {label}"
            assert m.calculated_percentile == percentile, (
                f"Wrong percentile for {label}"
            )

    def test_parse_femur_specifically(self, parser, sample_fetus_data):
        """Test that Femur is parsed correctly (addressing user's concern)."""
        result = parser.parse(sample_fetus_data)

        femur = result.get_measurement_by_label("Femur")
        assert femur is not None, "Femur measurement not found!"
        assert femur.label == "Femur"
        assert femur.value == 5.01
        assert femur.calculated_percentile == 46.8
        assert femur.calculated_ega == 27.1

    def test_parse_nuchal_and_cerebellum(self, parser, sample_fetus_data):
        """Test that Nuchal Fold and Cerebellum are parsed (addressing user's concern)."""
        result = parser.parse(sample_fetus_data)

        # Nuchal Fold
        nuchal = result.get_measurement_by_label("Nuchal Fold")
        assert nuchal is not None, "Nuchal Fold not found!"
        assert nuchal.label == "Nuchal Fold"
        assert nuchal.value == 1.0

        # Cerebellum
        cerebellum = result.get_measurement_by_label("Cerebellum")
        assert cerebellum is not None, "Cerebellum not found!"
        assert cerebellum.label == "Cerebellum"
        assert cerebellum.value == 3.0
        assert cerebellum.calculated_ega == 27.4

    def test_parse_missing_measurements_key(self, parser):
        """Test error handling when 'measurements' key is missing."""
        invalid_data = {"fetus": {"fetus_number": 1}}

        with pytest.raises(ValueError, match="Did not find 'measurements'"):
            parser.parse(invalid_data)

    def test_parse_empty_measurements(self, parser):
        """Test parsing with empty measurements list."""
        data = {"fetus": {"fetus_number": 1}, "measurements": []}

        result = parser.parse(data)
        assert result.measurement_count == 0

    def test_parse_without_fetus_key(self, parser):
        """Test parsing when 'fetus' key is missing (should default to fetus_number=1)."""
        data = {
            "measurements": [
                {
                    "label": "AC",
                    "value": 22.62,
                    "unit_of_measure": "cm",
                    "calculated_percentile": 55.6,
                    "calculated_z_score": 0,
                    "calculated_ega": 26.9,
                    "fetus_number": 1,
                }
            ]
        }

        result = parser.parse(data)
        assert result.fetus_number == 1  # Should default to 1
        assert result.measurement_count == 1


class TestRealWorldData:
    """Test with actual data structure from Apple_Sally_pretty.json."""

    def test_parse_sally_apple_data(self):
        """Test parsing the actual JSON structure."""
        import json

        # This test requires the actual file
        # In a real test suite, you might use a fixture file
        try:
            with open("Apple_Sally_pretty.json", "r") as f:
                data = json.load(f)

            parser = MeasurementsParser()
            fetus_1 = data["fetuses"][0]
            result = parser.parse(fetus_1)

            # Verify basic structure
            assert result.fetus_number == 1
            assert result.measurement_count == 6

            # Verify specific measurements
            ac = result.get_measurement_by_label("AC")
            assert ac.value == 22.62
            assert ac.calculated_percentile == 55.6

            femur = result.get_measurement_by_label("Femur")
            assert femur is not None
            assert femur.value == 5.01

        except FileNotFoundError:
            pytest.skip("Apple_Sally_pretty.json not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
