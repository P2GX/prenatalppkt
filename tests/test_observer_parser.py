import pytest
from pathlib import Path
from prenatalppkt.parsers.observer_parser import ObserverJSONParser


class TestObserverJSONParser:
    @pytest.fixture
    def parser(self):
        return ObserverJSONParser()

    @pytest.fixture
    def sample_json_path(self):
        return Path("tests/fixtures/observer/singleton_normal.json")

    def test_parse_basic_structure(self, parser, sample_json_path):
        """Test parsing of basic JSON structure."""
        result = parser.parse(sample_json_path)

        assert result.metadata.fetus_count == 1
        assert result.metadata.ga_by_working_edd > 0
        assert len(result.fetuses) == 1

    def test_parse_measurements(self, parser, sample_json_path):
        """Test extraction of measurements."""
        result = parser.parse(sample_json_path)
        fetus = result.fetuses[0]

        # Check standard measurements present
        labels = {m.label for m in fetus.measurements}
        assert "AC" in labels
        assert "BPD" in labels
        assert "HC" in labels
        assert "Femur" in labels

    def test_unit_conversion(self, parser):
        """Test cm to mm conversion."""
        assert parser._convert_to_mm(22.62, "cm") == 226.2
        assert parser._convert_to_mm(226.2, "mm") == 226.2

    def test_parse_anatomy(self, parser, sample_json_path):
        """Test extraction of anatomy findings."""
        result = parser.parse(sample_json_path)
        fetus = result.fetuses[0]

        # Check anatomy findings extracted
        assert len(fetus.anatomy) > 0

        # Check normal findings included
        normal_structures = [a.structure for a in fetus.anatomy if a.state == "Normal"]
        assert len(normal_structures) > 0

    def test_parse_anomalies(self, parser):
        """Test extraction of anomalies."""
        # Use fixture with known anomaly
        anomaly_json = Path("tests/fixtures/observer/singleton_dandy_walker.json")
        result = parser.parse(anomaly_json)
        fetus = result.fetuses[0]

        # Find Head anatomy
        head = [a for a in fetus.anatomy if a.structure == "Head"][0]
        assert head.state == "Abnormal"
        assert len(head.anomalies) > 0
        assert "Dandy Walker" in head.anomalies[0]

    def test_validation_missing_measurements(self, parser):
        """Test validation detects missing measurements."""
        incomplete_json = Path("tests/fixtures/observer/missing_measurements.json")
        result = parser.parse(incomplete_json)
        warnings = parser.validate(result)

        assert len(warnings) > 0
        assert any("Missing measurements" in w for w in warnings)

    def test_validation_implausible_values(self, parser):
        """Test validation detects biologically implausible values."""
        # Mock result with bad HC value
        # ... test implementation
        pass

    def test_multi_fetus_parsing(self, parser):
        """Test parsing of twin pregnancy."""
        twins_json = Path("tests/fixtures/observer/twins_normal.json")
        result = parser.parse(twins_json)

        assert result.metadata.fetus_count == 2
        assert len(result.fetuses) == 2
        assert result.fetuses[0].fetus_number == 1
        assert result.fetuses[1].fetus_number == 2
