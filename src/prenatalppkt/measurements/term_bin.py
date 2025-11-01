"""Core data structures for percentile-to-HPO mapping."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PercentileRange:
    """
    Represents a percentile range with min/max boundaries.

    Attributes:
        min_percentile: Lower boundary (inclusive)
        max_percentile: Upper boundary (exclusive)

    Example:
        >>> prange = PercentileRange(3.0, 5.0)
        >>> prange.contains(4.3)
        True
        >>> prange.contains(5.0)
        False
    """

    min_percentile: float
    max_percentile: float

    def contains(self, percentile: float) -> bool:
        """
        Check if percentile falls within this range.

        Args:
            percentile: Value to check (0-100)

        Returns:
            True if min_percentile <= percentile < max_percentile
        """
        return self.min_percentile <= percentile < self.max_percentile

    def __str__(self) -> str:
        """Return string representation."""
        return f"({self.min_percentile},{self.max_percentile})"


@dataclass
class TermBin:
    """
    HPO term mapped to a percentile range.

    Attributes:
        range: PercentileRange this bin covers
        hpo_id: HPO identifier (e.g., "HP:0000252")
        hpo_label: Human-readable label
        normal: True if this represents a normal finding

    Example:
        >>> prange = PercentileRange(3.0, 5.0)
        >>> bin_obj = TermBin(
        ...     range=prange,
        ...     hpo_id="HP:0040195",
        ...     hpo_label="Decreased head circumference",
        ...     normal=False
        ... )
        >>> bin_obj.fits(4.3)
        True
    """

    range: PercentileRange
    hpo_id: str
    hpo_label: str
    normal: bool

    def fits(self, percentile: float) -> bool:
        """
        Check if a percentile value belongs to this bin.

        Args:
            percentile: Value to check (0-100)

        Returns:
            True if percentile falls in this bin's range
        """
        return self.range.contains(percentile)

    @property
    def category(self) -> str:
        """
        Derive category from range boundaries.

        Maps to standard terminology based on percentile thresholds:
        - 0-3: lower_extreme_term
        - 3-5: lower_term
        - 5-10: abnormal_term (lower)
        - 10-90: normal_term
        - 90-95: abnormal_term (upper)
        - 95-97: upper_term
        - 97-100: upper_extreme_term

        Returns:
            Category string for provenance/reporting
        """
        r = self.range
        if r.max_percentile <= 3:
            return "lower_extreme_term"
        if r.max_percentile <= 5:
            return "lower_term"
        if r.max_percentile <= 10:
            return "abnormal_term"
        if r.max_percentile <= 90:
            return "normal_term"
        if r.max_percentile <= 95:
            return "abnormal_term"
        if r.max_percentile <= 97:
            return "upper_term"
        return "upper_extreme_term"
