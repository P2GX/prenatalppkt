"""
test_term_bin.py - Tests for PercentileRange and TermBin
"""

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

    def test_loinc_and_value_fields_default_to_none(self):
        """LOINC + raw-value fields default to None for back-compat."""
        bin = TermBin(
            range=PercentileRange.between_10p_50p(),
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=True,
        )

        assert bin.loinc_code is None
        assert bin.loinc_label is None
        assert bin.value_mm is None
        assert bin.gestational_age_weeks is None

    def test_loinc_and_value_fields_round_trip(self):
        """Optional LOINC + raw-value fields are stored and equality-relevant."""
        prange = PercentileRange.between_50p_90p()
        bin_a = TermBin(
            range=prange,
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=True,
            loinc_code="LOINC:11984-2",
            loinc_label="Fetal Head Circumference US",
            value_mm=175.0,
            gestational_age_weeks=20.3,
        )
        bin_b = TermBin(
            range=prange,
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=True,
            loinc_code="LOINC:11984-2",
            loinc_label="Fetal Head Circumference US",
            value_mm=175.0,
            gestational_age_weeks=20.3,
        )
        bin_c = TermBin(
            range=prange,
            hpo_id="HP:0000240",
            hpo_label="Abnormality of skull size",
            normal=True,
            loinc_code="LOINC:11984-2",
            loinc_label="Fetal Head Circumference US",
            value_mm=180.0,
            gestational_age_weeks=20.3,
        )

        assert bin_a.loinc_code == "LOINC:11984-2"
        assert bin_a.value_mm == 175.0
        assert bin_a.gestational_age_weeks == 20.3
        assert bin_a == bin_b
        assert bin_a != bin_c
