"""Tests for FetusDataBuilder"""

from prenatalppkt.dto.observer.builders.fetus_data_builder import FetusDataBuilder
from prenatalppkt.dto.observer.builders.fetus_anatomy_data import FetusAnatomyData
from prenatalppkt.dto.observer.builders.fetus_biometry_data import FetusBiometryData
from prenatalppkt.dto.observer.fetuses.fetus_core_data import FetusCoreData


def test_builder_with_core_only():
    """Test builder with just core data"""
    core = FetusCoreData(fetus_number=1)
    builder = FetusDataBuilder(core)
    fetus_data = builder.build()

    assert fetus_data is not None
    assert fetus_data.anatomy is None
    assert fetus_data.biometry is None


def test_builder_with_anatomy():
    """Test builder with anatomy data"""
    core = FetusCoreData(fetus_number=1)
    anatomy = FetusAnatomyData(
        hpo_terms=[], anatomy_text="Normal anatomy", anatomy=[], impression=None
    )

    builder = FetusDataBuilder(core)
    builder.with_anatomy(anatomy)
    fetus_data = builder.build()

    assert fetus_data.anatomy is not None
    assert fetus_data.anatomy.anatomy_text == "Normal anatomy"


def test_builder_with_biometry():
    """Test builder with biometry data"""
    core = FetusCoreData(fetus_number=1)
    biometry = FetusBiometryData(measurements=None, ratios=None, efws=None)

    builder = FetusDataBuilder(core)
    builder.with_biometry(biometry)
    fetus_data = builder.build()

    assert fetus_data.biometry is not None
