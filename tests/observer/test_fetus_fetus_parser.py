import pytest


class TestFetusFetusParser:
    """Tests for FetusFetusParser class"""

    def test_contains(self):
        """Test percentile containment check."""
        prange = PercentileRange(min_percentile=10.0, max_percentile=50.0)

        assert prange.contains(10.0) is True

    @pytest.mark.skip(
        reason="from_yaml_key() removed in new architecture - ranges come directly from YAML as {min, max} dicts"
    )
    def test_from_yaml_key(self):
        """
        Test parsing YAML keys.

        NOTE: This method no longer exists. In the new architecture,
        ranges are defined directly in YAML as:
          - min: 0
            max: 3
        Instead of string keys like "(0,3)".
        """
        pass
