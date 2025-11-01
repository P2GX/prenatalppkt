import pytest
from prenatalppkt.parser.observer.fetus import FetusFetusParser


@pytest.fixture
def parsed_json():
    """Provide the full mock of the 'fetus' JSON subfield directly as a Python dict."""
    return {
        "anatomy_text": "The cerebellum appeared abnormal. There was a neural tube defect.",
        "echo_text": "",
        "estimated_fetal_weight": 0,
        "fetal_echo_cardiac_axis_degrees": 0,
        "fetal_echo_performed": 0,
        "fetus_death": 0,
        "fetus_growth": "Unspecified",
        "fetus_number": 1,
        "fetus_presentation": "Vertex",
        "fetus_reduced": 0,
        "fetus_seen": 1,
        "ga_by_sonography": 27,
        "gender": "Unspecified",
        "heart_bpm": 150,
        "heart_movement_seen": "Seen",
        "heart_rate_is": "Regular",
        "impression_text": "Singleton IUP Dandy Walker",
        "multi_fetus_position_anterior_posterior": "Unspecified",
        "multi_fetus_position_left_right": "Unspecified",
        "multi_fetus_position_supine": "Unspecified",
        "use_early_anatomy_text": 0,
    }


@pytest.fixture
def fetus_fetus_parser(hpo_cr) -> FetusFetusParser:
    """Return an instance of FetusFetusParser wired to the shared HPO concept recognizer."""
    return FetusFetusParser(hpo_cr)


class TestFetusFetusParser:
    """Tests for FetusFetusParser class."""

    def test_anatomy_text(self, fetus_fetus_parser, parsed_json):
        """Ensure parser can process the anatomy_text content."""
        data = fetus_fetus_parser.parse(parsed_json)
        assert data is not None
        assert "hpo_hits" in data
        hpo_hits = data.get("hpo_hits")
        assert hpo_hits is not None
        assert len(hpo_hits) == 1
        hpo_hit = hpo_hits[0]
        assert hpo_hit.hpo_label == "Neural tube defect"

        # TODO: when FetusData supports phenotype capture,
        # assert that expected HPO concepts are found, e.g.:
        # assert any("neural tube defect" in hit["term"].lower() for hit in data.phenotypes)
