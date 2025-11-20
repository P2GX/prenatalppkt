"""Core data structures for percentile-to-HPO mapping."""

from __future__ import annotations

from prenatalppkt.hpo.simple_term import SimpleTerm
from prenatalppkt.measurements.percentile_range import PercentileRange


class TermBin:
    """
    HPO term mapped to a percentile range.

    Attributes:
        range: PercentileRange this bin covers
        hpo_id: HPO identifier (e.g., "HP:0000252")
        hpo_label: Human-readable label
        normal: True if this represents a normal finding
        description: str
    """

    def __init__(
        self,
        range: PercentileRange,
        hpo_id: str,
        hpo_label: str,
        normal: bool,
        description: str = "",
    ):
        self.range = range
        self.hpo_id = hpo_id
        self.hpo_label = hpo_label
        self.normal = bool(normal)
        self.description = description

    @staticmethod
    def from_term(
        range: PercentileRange, term: SimpleTerm, normal: bool, description: str = ""
    ) -> "TermBin":
        """
        Create a TermBin from a SimpleTerm and percentile range.

        Parameters
        ----------
        range : PercentileRange
            Percentile interval covered by this bin.
        term : SimpleTerm
            HPO term providing ID and label.
        normal : bool
            Whether this bin represents a normal finding.
        description : str, optional
            Free-text description of the measurement context.

        Returns
        -------
        TermBin
            The constructed term bin.
        """
        return TermBin(
            range=range,
            hpo_id=term.hpo_id,
            hpo_label=term.hpo_label,
            normal=normal,
            description=description,
        )

    def fits(self, percentile: float) -> bool:
        """
        Return True if a percentile value falls within this bin's range.

        Parameters
        ----------
        percentile : float
            Raw percentile value.

        Returns
        -------
        bool
            Whether the percentile is contained in this bin.
        """
        return self.range.contains(percentile)

    @property
    def category(self) -> str:
        """
        Return a coarse-grained label describing the percentile interval (e.g., 'normal_term', 'lower_extreme_term'). This category is used when grouping term bins for interpretation.
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

    def __repr__(self) -> str:
        return (
            f"TermBin(range={self.range!r}, "
            f"hpo_id={self.hpo_id!r}, "
            f"hpo_label={self.hpo_label!r}, "
            f"normal={self.normal!r}, "
            f"description={self.description!r})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, TermBin):
            return False
        return (
            self.range == other.range
            and self.hpo_id == other.hpo_id
            and self.hpo_label == other.hpo_label
            and self.normal == other.normal
            and self.description == other.description
        )
