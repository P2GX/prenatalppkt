import pytest
from pathlib import Path
from prenatalppkt.parsers.observer_parser import ObserverJSONParser
from prenatalppkt.parsers.observer_integration import ObserverPhenotypicConverter


class TestObserverIntegration:
    @pytest.fixture
    def converter(self):
        return ObserverPhenotypicConverter(reference_source="intergrowth")

    def test_convert_to_observations(self, converter):
        """Test conversion of parsed data to TermObservations."""
        parser = ObserverJSONParser()
        parsed = parser.parse(Path("tests/fixtures/observer/singleton_normal.json"))

        observations = converter.convert(parsed)

        # Should have observations for each measurement
        assert len(observations) >= 4  # AC, BPD, HC, FL minimum

        # Check observation structure
        obs = observations[0]
        assert obs.hpo_id.startswith("HP:")
        assert obs.hpo_label is not None
        assert obs.gestational_age.weeks > 0
        assert obs.percentile is not None

    def test_microcephaly_detection(self, converter):
        """Test that low HC is correctly mapped to Microcephaly."""
        parser = ObserverJSONParser()
        parsed = parser.parse(
            Path("tests/fixtures/observer/singleton_microcephaly.json")
        )

        observations = converter.convert(parsed)

        # Find HC observation
        hc_obs = [o for o in observations if "head_circumference" in str(o)][0]
        assert hc_obs.hpo_id == "HP:0000252"  # Microcephaly
        assert hc_obs.observed == True
        assert hc_obs.percentile < 3
