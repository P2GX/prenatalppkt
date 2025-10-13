import typing
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.measurement_result import MeasurementResult


class ReferenceRange:
    """
    Defines the percentile thresholds for a particular gestational age and
    provides logic to evaluate raw measurement values against these thresholds.

    The evaluation logic is designed to be flexible - allowing external
    configuration of percentile bins (e.g., "abnormal" = 3-10th, 90-97th)
    through the class interface or JSON configuration in the future.

    Attributes
    ----------
    _gestational_age : GestationalAge
        Gestational age for which these thresholds apply.
    _percentile_thresholds : list[float]
        Numeric thresholds (ascending order) defining key percentiles.
    """

    _gestational_age: GestationalAge
    _percentile_thresholds: typing.List[float]

    def __init__(
        self, gestational_age: GestationalAge, percentiles: typing.List[float]
    ) -> None:
        self._gestational_age = gestational_age
        self._percentile_thresholds = percentiles

    @property
    def gestational_age(self) -> GestationalAge:
        """Return the gestational age for this reference range."""
        return self._gestational_age

    @property
    def percentile_thresholds(self) -> typing.List[float]:
        """Return the percentile thresholds as a list (3rd-97th inclusive)."""
        return self._percentile_thresholds

    def evaluate(self, value: float) -> MeasurementResult:
        """
        Compare a measurement value against percentile thresholds and return a
        corresponding MeasurementResult.

        Notes
        -----
        The thresholds list should contain percentiles in ascending order:
        [3rd, 5th, 10th, 50th, 90th, 95th, 97th]
        """

        p = self._percentile_thresholds
        if value <= p[0]:
            return MeasurementResult.below_3p()
        elif value <= p[1]:
            return MeasurementResult.between_3p_5p()
        elif value <= p[2]:
            return MeasurementResult.between_5p_10p()
        elif value <= p[3]:
            return MeasurementResult.between_10p_50p()
        elif value <= p[4]:
            return MeasurementResult.between_50p_90p()
        elif value <= p[5]:
            return MeasurementResult.between_90p_95p()
        elif value <= p[6]:
            return MeasurementResult.between_95p_97p()
        else:
            return MeasurementResult.above_97p()
