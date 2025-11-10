"""
test_term_bin.py - Tests for PercentileRange and TermBin
"""

import pytest
from prenatalppkt.measurements.term_bin import PercentileRange, TermBin


class TestPercentileRange:
    """Tests for PercentileRange class."""

    def test_contains_inside_range(self):
        """Test percentile inside range."""
        prange = PercentileRange(3, 5)
        assert prange.contains(3.0) is True
        assert prange.contains(4.3) is True
        assert prange.contains(4.999) is True

    def test_contains_outside_range(self):
        """Test percentile outside range."""
        prange = PercentileRange(3, 5)
        assert prange.contains(2.9) is False
        assert prange.contains(5.0) is False  # Upper bound exclusive
        assert prange.contains(5.1) is False

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


class TestTermBin:
    """Tests for TermBin class."""

    def test_fits(self):
        """Test TermBin.fits() method."""
        prange = PercentileRange(3, 5)
        bin = TermBin(
            range=prange,
            hpo_id="HP:0040195",
            hpo_label="Decreased head circumference",
            normal=False,
        )

        assert bin.fits(4.3) is True
        assert bin.fits(2.9) is False
        assert bin.fits(5.0) is False

    def test_category_lower_extreme(self):
        """Test category for lower extreme range."""
        prange = PercentileRange(0, 3)
        bin = TermBin(prange, "HP:0000252", "Microcephaly", False)
        assert bin.category == "lower_extreme_term"

    def test_category_normal(self):
        """Test category for normal range."""
        prange = PercentileRange(10, 50)
        bin = TermBin(prange, "HP:0000240", "Normal", True)
        assert bin.category == "normal_term"

    def test_category_upper_extreme(self):
        """Test category for upper extreme range."""
        prange = PercentileRange(97, 100)
        bin = TermBin(prange, "HP:0000256", "Macrocephaly", False)
        assert bin.category == "upper_extreme_term"
