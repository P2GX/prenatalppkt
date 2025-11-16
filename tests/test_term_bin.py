"""
test_term_bin.py - Tests for PercentileRange and TermBin
"""

import pytest
from prenatalppkt.measurements.percentile import Percentile
from prenatalppkt.measurements.term_bin import PercentileRange, TermBin



class TestTermBin:
    """Tests for TermBin class."""

    def test_fits(self):
        """Test TermBin.fits() method."""
        prange = PercentileRange.between_3p_5p()
        bin = TermBin(
            range=prange,
            hpo_id="HP:0040195",
            hpo_label="Decreased head circumference",
            normal=False,
        )

        assert bin.range.lower == Percentile.Third
        assert bin.range.upper == Percentile.Fifth

    def test_category_lower_extreme(self):
        """Test category for lower extreme range."""
        prange = PercentileRange.below_3p()
        assert prange.lower is None

    def test_category_normal(self):
        """Test category for normal range."""
        prange = PercentileRange.between_10p_50p()
        assert prange.lower == Percentile.Tenth
        assert prange.upper == Percentile.Fiftieth

    def test_category_upper_extreme(self):
        """Test category for upper extreme range."""
        prange = PercentileRange.above_97p()
        assert prange.upper is None
        assert prange.lower == Percentile.Ninetyseventh
