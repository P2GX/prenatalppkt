import typing
from prenatalppkt.measurements.percentile import Percentile


class MeasurementResult:
    """
    Represents the outcome of comparing a measured biometric value against percentile reference thresholds.

    A MeasurementResult does not store the raw measurement; it only encodes the percentile bin in which the measurement falls.
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

    # --- Convenience Static constructors for percentile intervals --- #

    @staticmethod
    def below_3p() -> "MeasurementResult":
        """
        Percentile bin for less than 3rd Percentile.
        """
        return MeasurementResult(lower=None, upper=Percentile.Third)

    @staticmethod
    def between_3p_5p() -> "MeasurementResult":
        """
        Percentile bin for between 3rd and 5th Percentiles.
        """
        return MeasurementResult(lower=Percentile.Third, upper=Percentile.Fifth)

    @staticmethod
    def between_5p_10p() -> "MeasurementResult":
        """
        Percentile bin for between 5th and 10th Percentiles.
        """
        return MeasurementResult(lower=Percentile.Fifth, upper=Percentile.Tenth)

    @staticmethod
    def between_10p_50p() -> "MeasurementResult":
        """
        Percentile bin for between 10th and 50th Percentiles.
        """
        return MeasurementResult(lower=Percentile.Tenth, upper=Percentile.Fiftieth)

    @staticmethod
    def between_50p_90p() -> "MeasurementResult":
        """
        Percentile bin for between 50th and 90th Percentiles.
        """
        return MeasurementResult(lower=Percentile.Fiftieth, upper=Percentile.Ninetieth)

    @staticmethod
    def between_90p_95p() -> "MeasurementResult":
        """
        Percentile bin for between 90th and 95th Percentiles.
        """
        return MeasurementResult(
            lower=Percentile.Ninetieth, upper=Percentile.Ninetyfifth
        )

    @staticmethod
    def between_95p_97p() -> "MeasurementResult":
        """
        Percentile bin for between 95th and 97th Percentiles.
        """
        return MeasurementResult(
            lower=Percentile.Ninetyfifth, upper=Percentile.Ninetyseventh
        )

    @staticmethod
    def above_97p() -> "MeasurementResult":
        """
        Percentile bin for more than 97th Percentile.
        """
        return MeasurementResult(lower=Percentile.Ninetyseventh, upper=None)

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
