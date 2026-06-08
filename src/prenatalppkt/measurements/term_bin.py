"""
Core data structures for percentile-to-HPO mapping.
"""

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
        loinc_code: Optional LOINC identifier for the raw measurement (e.g., "LOINC:11984-2")
        loinc_label: Optional human-readable LOINC label
        value_mm: Optional raw measurement value in millimeters
        gestational_age_weeks: Optional gestational age at observation in fractional weeks
    """

    def __init__(
        self,
        range: PercentileRange,
        hpo_id: str,
        hpo_label: str,
        normal: bool,
        description: str = "",
        loinc_code: str | None = None,
        loinc_label: str | None = None,
        value_mm: float | None = None,
        gestational_age_weeks: float | None = None,
    ):
        self.range = range
        self.hpo_id = hpo_id
        self.hpo_label = hpo_label
        self.normal = bool(normal)
        self.description = description
        self.loinc_code = loinc_code
        self.loinc_label = loinc_label
        self.value_mm = value_mm
        self.gestational_age_weeks = gestational_age_weeks

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
        Use PercentileRange.contains() so bins are correctly matched by numeric percentile rather than bin_key comparison.
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
            f"description={self.description!r}, "
            f"loinc_code={self.loinc_code!r}, "
            f"loinc_label={self.loinc_label!r}, "
            f"value_mm={self.value_mm!r}, "
            f"gestational_age_weeks={self.gestational_age_weeks!r})"
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
            and self.loinc_code == other.loinc_code
            and self.loinc_label == other.loinc_label
            and self.value_mm == other.value_mm
            and self.gestational_age_weeks == other.gestational_age_weeks
        )
