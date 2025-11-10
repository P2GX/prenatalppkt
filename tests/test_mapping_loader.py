"""
test_mapping_loader.py - Tests for BiometryMappingLoader
"""

import pytest
from pathlib import Path
from prenatalppkt.mapping_loader import BiometryMappingLoader


def test_load_mappings():
    """Test loading mappings from YAML."""
    yaml_path = Path("data/mappings/biometry_hpo_mappings.yaml")

    if not yaml_path.exists():
        pytest.skip("YAML file not found")

    mappings = BiometryMappingLoader.load(yaml_path)

    # Check all measurement types present
    assert "head_circumference" in mappings
    assert "biparietal_diameter" in mappings
    assert "femur_length" in mappings
    assert "abdominal_circumference" in mappings
    assert "occipitofrontal_diameter" in mappings

    # Check HC has 8 bins
    hc_bins = mappings["head_circumference"]
    assert len(hc_bins) == 8

    # Check first bin structure
    first_bin = hc_bins[0]
    assert first_bin.range.min_percentile == 0
    assert first_bin.range.max_percentile == 3
    assert first_bin.hpo_id == "HP:0000252"
    assert first_bin.hpo_label == "Microcephaly"
    assert first_bin.normal is False

    # Check bins are sorted
    for i in range(len(hc_bins) - 1):
        assert hc_bins[i].range.min_percentile <= hc_bins[i + 1].range.min_percentile


def test_load_nonexistent_file():
    """Test error handling for missing file."""
    with pytest.raises(FileNotFoundError):
        BiometryMappingLoader.load(Path("nonexistent.yaml"))
