"""Direct boundary tests for PercentileRange.evaluate() / .contains().

This is the single function every biometry measurement in the whole
pipeline passes through (via TermBin.fits() -> PercentileRange.contains()),
but until now it had no dedicated test at all - only indirect coverage
via tests/test_reference_range.py, whose test values all sit comfortably
inside a bin (140.0, 146.0, ...) rather than at an exact boundary
(3.0, 5.0, 10.0, ...), where inclusive/exclusive semantics actually
matter. This file exists to close that gap.
"""

import pytest

from prenatalppkt.measurements.percentile_range import PercentileRange

# The 9 numbers where bin membership changes: 0 (the floor), the 7 real
# cutoffs, and 100 (the ceiling).
BOUNDARIES = [0.0, 3.0, 5.0, 10.0, 50.0, 90.0, 95.0, 97.0, 100.0]

EXPECTED_BIN_AT_BOUNDARY = {
    # A boundary value belongs to the bin that STARTS at that number
    # (lower bound is inclusive) - confirmed against evaluate()'s own
    # source, not guessed.
    0.0: "below_3p",
    3.0: "between_3p_5p",
    5.0: "between_5p_10p",
    10.0: "between_10p_50p",
    50.0: "between_50p_90p",
    90.0: "between_90p_95p",
    95.0: "between_95p_97p",
    97.0: "above_97p",
    100.0: "above_97p",
}


@pytest.mark.parametrize("boundary", BOUNDARIES)
def test_evaluate_at_exact_boundary(boundary):
    """evaluate() at each exact cutoff value lands in the bin that
    starts there, not the one that ends there."""
    result = PercentileRange.evaluate(boundary)
    assert result.bin_key == EXPECTED_BIN_AT_BOUNDARY[boundary]


@pytest.mark.parametrize("boundary", BOUNDARIES)
def test_contains_agrees_with_evaluate_at_boundary(boundary):
    """contains() must agree with evaluate() at every boundary - if
    these ever disagreed, TermBin.fits() (which calls contains()) could
    pick a different bin than evaluate() would have, for the exact same
    number."""
    result = PercentileRange.evaluate(boundary)
    assert result.contains(boundary) is True


@pytest.mark.parametrize("boundary", [3.0, 5.0, 10.0, 50.0, 90.0, 95.0, 97.0])
def test_value_just_below_boundary_stays_in_the_lower_bin(boundary):
    """A value a tiny bit below a cutoff must NOT be pulled into the
    bin that starts at the cutoff."""
    just_below = boundary - 0.01
    result = PercentileRange.evaluate(just_below)
    assert result.bin_key != EXPECTED_BIN_AT_BOUNDARY[boundary]
    assert result.contains(boundary) is False


def test_evaluate_rejects_out_of_range_percentile():
    with pytest.raises(ValueError):
        PercentileRange.evaluate(-0.01)
    with pytest.raises(ValueError):
        PercentileRange.evaluate(100.01)
