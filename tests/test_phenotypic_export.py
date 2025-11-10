"""
test_term_bin.py - Tests for TermBin and PercentileRange
"""

import pytest
from prenatalppkt.measurements.term_bin import TermBin, PercentileRange


class TestPercentileRange:
    """Tests for PercentileRange."""

    def test_contains(self):
        """Test percentile containment check."""
        prange = PercentileRange(min_percentile=10.0, max_percentile=50.0)

        assert prange.contains(10.0) is True
        assert prange.contains(30.0) is True
        assert prange.contains(50.0) is False  # Upper bound exclusive
        assert prange.contains(9.9) is False
        assert prange.contains(50.1) is False

    def test_contains_edge_cases(self):
        """Test edge cases for contains method."""
        prange = PercentileRange(min_percentile=0.0, max_percentile=3.0)

        assert prange.contains(0.0) is True  # Lower bound inclusive
        assert prange.contains(1.5) is True
        assert prange.contains(2.9) is True
        assert prange.contains(3.0) is False  # Upper bound exclusive
        assert prange.contains(-0.1) is False

    def test_boundary_values(self):
        """Test boundary behavior across different ranges."""
        # Test (3, 5) range
        prange_3_5 = PercentileRange(min_percentile=3.0, max_percentile=5.0)
        assert prange_3_5.contains(3.0) is True
        assert prange_3_5.contains(4.0) is True
        assert prange_3_5.contains(5.0) is False

        # Test (90, 95) range
        prange_90_95 = PercentileRange(min_percentile=90.0, max_percentile=95.0)
        assert prange_90_95.contains(89.9) is False
        assert prange_90_95.contains(90.0) is True
        assert prange_90_95.contains(92.5) is True
        assert prange_90_95.contains(95.0) is False

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
    """Tests for TermBin."""

    def test_init(self):
        """Test TermBin initialization."""
        prange = PercentileRange(min_percentile=0.0, max_percentile=3.0)
        term_bin = TermBin(
            range=prange, hpo_id="HP:0000252", hpo_label="Microcephaly", normal=False
        )

        assert term_bin.range == prange
        assert term_bin.hpo_id == "HP:0000252"
        assert term_bin.hpo_label == "Microcephaly"
        assert term_bin.normal is False

    def test_fits_method(self):
        """Test the fits method delegates to range.contains()."""
        prange = PercentileRange(min_percentile=10.0, max_percentile=50.0)
        term_bin = TermBin(
            range=prange, hpo_id="HP:0000001", hpo_label="Test term", normal=True
        )

        assert term_bin.fits(10.0) is True
        assert term_bin.fits(30.0) is True
        assert term_bin.fits(50.0) is False  # Upper bound exclusive
        assert term_bin.fits(9.9) is False

    def test_category_property(self):
        """Test that category is derived from range boundaries."""
        # Lower extreme: 0-3
        bin1 = TermBin(
            range=PercentileRange(0.0, 3.0),
            hpo_id="HP:0000252",
            hpo_label="Microcephaly",
            normal=False,
        )
        assert bin1.category == "lower_extreme_term"

        # Lower term: 3-5
        bin2 = TermBin(
            range=PercentileRange(3.0, 5.0),
            hpo_id="HP:0040195",
            hpo_label="Decreased head circumference",
            normal=False,
        )
        assert bin2.category == "lower_term"

        # Abnormal term: 5-10
        bin3 = TermBin(
            range=PercentileRange(5.0, 10.0),
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=False,
        )
        assert bin3.category == "abnormal_term"

        # Normal term: 10-50
        bin4 = TermBin(
            range=PercentileRange(10.0, 50.0),
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=True,
        )
        assert bin4.category == "normal_term"

        # Normal term: 50-90
        bin5 = TermBin(
            range=PercentileRange(50.0, 90.0),
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=True,
        )
        assert bin5.category == "normal_term"

        # Abnormal term: 90-95
        bin6 = TermBin(
            range=PercentileRange(90.0, 95.0),
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=False,
        )
        assert bin6.category == "abnormal_term"

        # Upper term: 95-97
        bin7 = TermBin(
            range=PercentileRange(95.0, 97.0),
            hpo_id="HP:0040194",
            hpo_label="Increased head circumference",
            normal=False,
        )
        assert bin7.category == "upper_term"

        # Upper extreme: 97-100
        bin8 = TermBin(
            range=PercentileRange(97.0, 100.0),
            hpo_id="HP:0000256",
            hpo_label="Macrocephaly",
            normal=False,
        )
        assert bin8.category == "upper_extreme_term"

    def test_normal_flag(self):
        """Test that normal flag is preserved."""
        prange = PercentileRange(10.0, 50.0)

        normal_bin = TermBin(
            range=prange,
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=True,
        )
        assert normal_bin.normal is True

        abnormal_bin = TermBin(
            range=prange,
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=False,
        )
        assert abnormal_bin.normal is False

    def test_multiple_bins_for_same_hpo(self):
        """Test that same HPO can be used in multiple bins (normal vs abnormal)."""
        hpo_id = "HP:0000240"
        hpo_label = "Abnormality of skull size"

        # Normal range bins
        normal_bin_lower = TermBin(
            range=PercentileRange(10.0, 50.0),
            hpo_id=hpo_id,
            hpo_label=hpo_label,
            normal=True,
        )

        normal_bin_upper = TermBin(
            range=PercentileRange(50.0, 90.0),
            hpo_id=hpo_id,
            hpo_label=hpo_label,
            normal=True,
        )

        # Abnormal range bin
        abnormal_bin = TermBin(
            range=PercentileRange(5.0, 10.0),
            hpo_id=hpo_id,
            hpo_label=hpo_label,
            normal=False,
        )

        assert normal_bin_lower.normal is True
        assert normal_bin_upper.normal is True
        assert abnormal_bin.normal is False

        # All share same HPO
        assert normal_bin_lower.hpo_id == normal_bin_upper.hpo_id == abnormal_bin.hpo_id

    def test_fits_boundary_behavior(self):
        """Test fits behavior at exact boundaries."""
        # Create bin for (10, 50) range
        bin_10_50 = TermBin(
            range=PercentileRange(10.0, 50.0),
            hpo_id="HP:0000001",
            hpo_label="Test",
            normal=True,
        )

        # Lower boundary: inclusive
        assert bin_10_50.fits(10.0) is True
        assert bin_10_50.fits(10.1) is True

        # Upper boundary: exclusive
        assert bin_10_50.fits(49.9) is True
        assert bin_10_50.fits(50.0) is False

        # Outside range
        assert bin_10_50.fits(9.9) is False
        assert bin_10_50.fits(50.1) is False


class TestTermBinIntegration:
    """Integration tests for TermBin with realistic scenarios."""

    def test_all_eight_bins_for_head_circumference(self):
        """Test complete set of 8 bins for head circumference."""
        bins = [
            TermBin(PercentileRange(0.0, 3.0), "HP:0000252", "Microcephaly", False),
            TermBin(
                PercentileRange(3.0, 5.0),
                "HP:0040195",
                "Decreased head circumference",
                False,
            ),
            TermBin(
                PercentileRange(5.0, 10.0),
                "HP:0000240",
                "Abnormality of skull size",
                False,
            ),
            TermBin(
                PercentileRange(10.0, 50.0),
                "HP:0000240",
                "Abnormality of skull size",
                True,
            ),
            TermBin(
                PercentileRange(50.0, 90.0),
                "HP:0000240",
                "Abnormality of skull size",
                True,
            ),
            TermBin(
                PercentileRange(90.0, 95.0),
                "HP:0000240",
                "Abnormality of skull size",
                False,
            ),
            TermBin(
                PercentileRange(95.0, 97.0),
                "HP:0040194",
                "Increased head circumference",
                False,
            ),
            TermBin(PercentileRange(97.0, 100.0), "HP:0000256", "Macrocephaly", False),
        ]

        # Test that each percentile finds exactly one bin
        test_percentiles = [1.5, 4.0, 7.5, 30.0, 70.0, 92.5, 96.0, 98.5]

        for percentile in test_percentiles:
            matching_bins = [b for b in bins if b.fits(percentile)]
            assert len(matching_bins) == 1, (
                f"Percentile {percentile} should match exactly 1 bin"
            )

        # Test that all bins have correct categories
        expected_categories = [
            "lower_extreme_term",
            "lower_term",
            "abnormal_term",
            "normal_term",
            "normal_term",
            "abnormal_term",
            "upper_term",
            "upper_extreme_term",
        ]

        for bin, expected_cat in zip(bins, expected_categories):
            assert bin.category == expected_cat

    def test_finding_appropriate_bin(self):
        """Test finding the appropriate bin for a given percentile."""
        bins = [
            TermBin(PercentileRange(0.0, 3.0), "HP:0000252", "Microcephaly", False),
            TermBin(PercentileRange(10.0, 50.0), "HP:0000240", "Normal", True),
            TermBin(PercentileRange(97.0, 100.0), "HP:0000256", "Macrocephaly", False),
        ]

        # Test finding bins
        assert bins[0].fits(1.5) is True  # Microcephaly
        assert bins[1].fits(30.0) is True  # Normal
        assert bins[2].fits(98.5) is True  # Macrocephaly

        # Test non-matching
        assert bins[0].fits(30.0) is False
        assert bins[1].fits(1.5) is False
        assert bins[2].fits(30.0) is False
