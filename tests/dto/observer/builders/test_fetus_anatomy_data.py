"""Tests for FetusAnatomyData"""

from prenatalppkt.dto.observer.builders.fetus_anatomy_data import FetusAnatomyData


def test_anatomy_data_creation():
    """Test creating FetusAnatomyData"""
    anatomy = FetusAnatomyData(
        hpo_terms=[],
        anatomy_text="Normal findings",
        anatomy=[{"finding": "normal"}],
        impression="Unremarkable",
    )

    assert anatomy.hpo_terms == []
    assert anatomy.anatomy_text == "Normal findings"
    assert len(anatomy.anatomy) == 1
    assert anatomy.impression == "Unremarkable"


def test_anatomy_data_minimal():
    """Test FetusAnatomyData with minimal fields"""
    anatomy = FetusAnatomyData(
        hpo_terms=[], anatomy_text=None, anatomy=None, impression=None
    )

    assert anatomy.hpo_terms == []
    assert anatomy.anatomy_text is None
