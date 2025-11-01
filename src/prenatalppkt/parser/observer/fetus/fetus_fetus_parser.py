import typing
from prenatalppkt.hpo import HpoConceptRecognizer
from prenatalppkt.dto import FetusData

"""
for the "fetus" subfield in the "fetus" superfield within the Observer JSON
"""

class FetusFetusParser:
    def __init__(self, hcr: HpoConceptRecognizer):
        self._hcr = hcr

import pytest, typing
from prenatalppkt.hpo import HpoParser
from prenatalppkt.dto import FetusData
from prenatalppkt.parser.observer.fetus_fetus_parser import FetusFetusParser


@pytest.fixture(scope="module")
def mock_hcr():
    """Use the real HpoConceptRecognizer from HpoParser."""
    parser = HpoParser()
    return parser.get_hpo_concept_recognizer()


@pytest.fixture
def sample_json():
    """Minimal mock of the expected Observer JSON subfield."""
    return {
        "XYZ": "The fetus shows microcephaly and abnormal femur length."
    }


def test_init_with_hcr(mock_hcr):
    """Ensure parser initializes correctly with an HPO recognizer."""
    parser = FetusFetusParser(mock_hcr)
    assert parser._hcr is mock_hcr


def test_raises_on_invalid_json(mock_hcr):
    """Expect ValueError if non-dict is passed."""
    parser = FetusFetusParser(mock_hcr)
    with pytest.raises(ValueError):
        parser.parse("not a dict")


def test_raises_on_missing_xyz(mock_hcr):
    """Expect ValueError if required key is missing."""
    parser = FetusFetusParser(mock_hcr)
    with pytest.raises(ValueError):
        parser.parse({})


def test_parses_hpo_terms(mock_hcr, sample_json):
    """Test that HPO terms are detected and mapped."""
    parser = FetusFetusParser(mock_hcr)
    result = parser.parse(sample_json)

    # TODO: Replace GOTTAFIXTHIS with real FetusData init before enabling this
    assert isinstance(result, FetusData)
    # When implemented, verify HPO hits were found
    # assert any("microcephaly" in hit.hpo_label.lower() for hit in result.phenotypes)
