import typing
import functools

from prenatalppkt.measurements.percentile import Percentile


@functools.total_ordering
class PercentileRange:
    """
    Represents the outcome of comparing a measured biometric value against percentile reference thresholds.

    A PercentileRange does not store the raw measurement; it only encodes the percentile bin in which the measurement falls.
    Higher-level evaluators should interpret whether an HPO term applies based on the metric considered as well as reference ranges.
    """

    _lower: typing.Optional[Percentile]
    _upper: typing.Optional[Percentile]

    def __init__(
        self, lower: typing.Optional[Percentile], upper: typing.Optional[Percentile]
    ) -> None:
        """Initialize the measurement result percentile range."""
        self._lower = lower
        self._upper = upper

    @property
    def lower(self) -> typing.Optional[Percentile]:
        """Return the lower percentile bound (or None)."""
        return self._lower

    @property
    def upper(self) -> typing.Optional[Percentile]:
        """Return the upper percentile bound (or None)."""
        return self._upper

    @property
    def bin_key(self) -> str:
        """
        Return a canonical bin label (e.g. 'below_3p', 'between_5p_10p', 'above_97p')
        that identifies the percentile interval of this measurement result.

        This property is used by higher-level evaluators (e.g., SonographicMeasurement)
        to map percentile ranges to HPO term categories.
        """
        mapping = {
            (None, Percentile.Third): "below_3p",
            (Percentile.Third, Percentile.Fifth): "between_3p_5p",
            (Percentile.Fifth, Percentile.Tenth): "between_5p_10p",
            (Percentile.Tenth, Percentile.Fiftieth): "between_10p_50p",
            (Percentile.Fiftieth, Percentile.Ninetieth): "between_50p_90p",
            (Percentile.Ninetieth, Percentile.Ninetyfifth): "between_90p_95p",
            (Percentile.Ninetyfifth, Percentile.Ninetyseventh): "between_95p_97p",
            (Percentile.Ninetyseventh, None): "above_97p",
        }
        return mapping.get((self._lower, self._upper), "unknown")

    def contains(self, perc: float) -> bool:
        """
        Return True if the numeric percentile belongs inside this PercentileRange.

        Boundaries follow the same semantics as evaluate():
        - lower bound is inclusive
        - upper bound is exclusive, except when upper=None (open ended)
        """
        if perc < 0 or perc > 100:
            return False

        # lower bound
        if self._lower is not None:
            if perc < self._lower.value_numeric:
                return False

        # upper bound
        if self._upper is not None:
            if perc >= self._upper.value_numeric:
                return False

        return True

    # --- Convenience Static constructors for percentile intervals --- #

    @staticmethod
    def below_3p() -> "PercentileRange":
        """
        Percentile bin for less than 3rd Percentile.
        """
        return PercentileRange(lower=None, upper=Percentile.Third)

    @staticmethod
    def between_3p_5p() -> "PercentileRange":
        """
        Percentile bin for between 3rd and 5th Percentiles.
        """
        return PercentileRange(lower=Percentile.Third, upper=Percentile.Fifth)

    @staticmethod
    def between_5p_10p() -> "PercentileRange":
        """
        Percentile bin for between 5th and 10th Percentiles.
        """
        return PercentileRange(lower=Percentile.Fifth, upper=Percentile.Tenth)

    @staticmethod
    def between_10p_50p() -> "PercentileRange":
        """
        Percentile bin for between 10th and 50th Percentiles.
        """
        return PercentileRange(lower=Percentile.Tenth, upper=Percentile.Fiftieth)

    @staticmethod
    def between_50p_90p() -> "PercentileRange":
        """
        Percentile bin for between 50th and 90th Percentiles.
        """
        return PercentileRange(lower=Percentile.Fiftieth, upper=Percentile.Ninetieth)

    @staticmethod
    def between_90p_95p() -> "PercentileRange":
        """
        Percentile bin for between 90th and 95th Percentiles.
        """
        return PercentileRange(lower=Percentile.Ninetieth, upper=Percentile.Ninetyfifth)

    @staticmethod
    def between_95p_97p() -> "PercentileRange":
        """
        Percentile bin for between 95th and 97th Percentiles.
        """
        return PercentileRange(
            lower=Percentile.Ninetyfifth, upper=Percentile.Ninetyseventh
        )

    @staticmethod
    def above_97p() -> "PercentileRange":
        """
        Percentile bin for more than 97th Percentile.
        """
        return PercentileRange(lower=Percentile.Ninetyseventh, upper=None)

    # ------------------------------------------------------------------ #
    # Default qualitative interpretation (simple 3-bin fallback)
    # ------------------------------------------------------------------ #
    @staticmethod
    def default_interpretation() -> typing.Dict[
        typing.Tuple[typing.Optional["Percentile"], typing.Optional["Percentile"]], str
    ]:
        """
        Return a minimal default mapping from percentile intervals to qualitative labels.

        This is a placeholder used by some early subclasses or experimental adapters
        (e.g., mapping only 'low' or 'high' extremes). The canonical eight-bin mapping
        and HPO assignment logic now live in YAML and `TermObservation`.

        Returns
        -------
        dict
            Mapping of (lower, upper) percentile tuple -> label string.
        """
        return {
            (None, Percentile.Third): "low",
            (Percentile.Ninetyseventh, None): "high",
        }

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        lower = self._lower.name if self._lower else "None"
        upper = self._upper.name if self._upper else "None"
        return f"MeasurementResult(lower={lower}, upper={upper})"

    @staticmethod
    def evaluate(perc: float) -> "PercentileRange":
        """
        Return the percentile interval (as a PercentileRange) corresponding to
        a numeric percentile value.

        Parameters
        ----------
        perc : float
            Percentile value between 0 and 100.

        Returns
        -------
        PercentileRange
            The matching percentile bin.

        Raises
        ------
        ValueError
            If the percentile is outside the 0-100 range.
        """
        if perc < 0:
            raise ValueError(f"Invalid percentile: {perc}")
        elif perc < 3.0:
            return PercentileRange.below_3p()
        elif perc < 5.0:
            return PercentileRange.between_3p_5p()
        elif perc < 10.0:
            return PercentileRange.between_5p_10p()
        elif perc < 50.0:
            return PercentileRange.between_10p_50p()
        elif perc < 90.0:
            return PercentileRange.between_50p_90p()
        elif perc < 95.0:
            return PercentileRange.between_90p_95p()
        elif perc < 97.0:
            return PercentileRange.between_95p_97p()
        elif perc <= 100:
            return PercentileRange.above_97p()
        else:
            raise ValueError(f"Invalid percentile: {perc}")

    def _sort_key(self) -> float:
        """
        Defines a numeric key for sorting / comparison.
        Uses upper if available, else uses a terminal value.
        """
        if self._upper is None:
            return 100.1
        return self._upper.value_numeric

    def __lt__(self, other):
        if not isinstance(other, PercentileRange):
            return NotImplemented
        return self._sort_key() < other._sort_key()

    def __eq__(self, other):
        if not isinstance(other, PercentileRange):
            return NotImplemented
        return self._lower == other._lower and self._upper == other._upper

    @staticmethod
    def from_min_max(min: int, max: int) -> "PercentileRange":
        """
        Construct a PercentileRange from explicit integer percentile bounds. This helper converts known (min, max) percentile intervals from the reference tables into the corresponding PercentileRange constructor (e.g., (0, 3) -> below_3p(), (10, 50) -> between_10p_50p()).

        Parameters
        ----------
        min : int
            Lower percentile bound.
        max : int
            Upper percentile bound.

        Returns
        -------
        PercentileRange
            The matching percentile interval.

        Raises
        ------
        ValueError
            If the (min, max) pair does not correspond to a supported percentile bin.
        """
        if min == 0 and max == 3:
            return PercentileRange.below_3p()
        elif min == 3 and max == 5:
            return PercentileRange.between_3p_5p()
        elif min == 5 and max == 10:
            return PercentileRange.between_5p_10p()
        elif min == 10 and max == 50:
            return PercentileRange.between_10p_50p()
        elif min == 50 and max == 90:
            return PercentileRange.between_50p_90p()
        elif min == 90 and max == 95:
            return PercentileRange.between_90p_95p()
        elif min == 95 and max == 97:
            return PercentileRange.between_95p_97p()
        elif min == 97 and max == 100:
            return PercentileRange.above_97p()
        else:
            raise ValueError(f"Unrecognized percentile range: ({min}-{max})")
