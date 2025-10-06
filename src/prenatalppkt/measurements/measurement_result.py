import typing
from prenatalppkt.measurements.percentile import Percentile


class MeasurementResult:
    """
    Represents the outcome of comparing a measured biometric value against
    percentile reference thresholds.

    A MeasurementResult does not store the raw measurement; it only encodes
    the percentile bin in which the measurement falls. This allows higher-level
    evaluators (e.g., SonographicMeasurement) to interpret whether an HPO term
    such as 'Decreased head circumference' or 'Abnormality of skull size' should apply.

    Attributes
    ----------
    _lower : Percentile | None
        The lower bound percentile for the measurement range.
    _upper : Percentile | None
        The upper bound percentile for the measurement range.
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

    # ---- Convenience constructors ---- #

    @staticmethod
    def below_3p() -> "MeasurementResult":
        """Return a result representing <3rd percentile."""
        return MeasurementResult(lower=None, upper=Percentile.Third)

    @staticmethod
    def between_3p_10p() -> "MeasurementResult":
        """Return a result representing 3rd-10th percentile."""
        return MeasurementResult(lower=Percentile.Third, upper=Percentile.Tenth)

    @staticmethod
    def between_10p_90p() -> "MeasurementResult":
        """Return a result representing 10th-90th percentile (normal range)."""
        return MeasurementResult(lower=Percentile.Tenth, upper=Percentile.Ninetieth)

    @staticmethod
    def between_90p_97p() -> "MeasurementResult":
        """Return a result representing 90th-97th percentile."""
        return MeasurementResult(
            lower=Percentile.Ninetieth, upper=Percentile.Ninetyseventh
        )

    @staticmethod
    def above_97p() -> "MeasurementResult":
        """Return a result representing >=97th percentile."""
        return MeasurementResult(lower=Percentile.Ninetyseventh, upper=None)

    # ---- Classification helpers ---- #

    def is_below_extreme(self) -> bool:
        """Return True if the measurement is <=3rd percentile."""
        return self._upper == Percentile.Third

    def is_above_extreme(self) -> bool:
        """Return True if the measurement is >=97th percentile."""
        return self._lower == Percentile.Ninetyseventh

    def is_abnormal(self) -> bool:
        """
        Return True if the measurement is between
        mildly abnormal ranges (3rd-10th or 90th-97th percentile).
        """
        if (self._lower, self._upper) in [
            (Percentile.Third, Percentile.Tenth),
            (Percentile.Ninetieth, Percentile.Ninetyseventh),
        ]:
            return True
        return False

    def __repr__(self) -> str:
        lower = self._lower.name if self._lower else "None"
        upper = self._upper.name if self._upper else "None"
        return f"MeasurementResult(lower={lower}, upper={upper})"
