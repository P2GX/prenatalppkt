"""
Unit tests for FetusCoreData DTO.
"""

from prenatalppkt.dto.fetuses.fetus_core_data import FetusCoreData


def test_fetus_core_data_repr():
    dto = FetusCoreData(
        fetus_number=1,
        gender="Female",
        ga_by_sonography=27.1,
        heart_bpm=140,
        fetus_presentation="Vertex",
    )
    s = repr(dto)
    assert "FetusCoreData" in s
    assert "number=1" in s
    assert "Vertex" in s
