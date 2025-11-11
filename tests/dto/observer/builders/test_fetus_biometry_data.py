"""Tests for FetusBiometryData"""

from prenatalppkt.dto.observer.builders.fetus_biometry_data import FetusBiometryData


def test_biometry_data_creation():
    """Test creating FetusBiometryData"""
    biometry = FetusBiometryData(measurements=None, ratios=None, efws=None)

    assert biometry.measurements is None
    assert biometry.ratios is None
    assert biometry.efws is None
