import typing

from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.measurement_result import MeasurementResult


class ReferenceRange:
    _gestational_age: GestationalAge
    _percentile_thresholds: typing.List[float]

    def __init__(
        self, gestational_age: GestationalAge, percentiles: typing.List[float]
    ) -> None:
        self._gestational_age = gestational_age
        self._percentile_thresholds = percentiles

    def evaluate(self, value: typing.Union[int, float]) -> MeasurementResult:
        if value < self._percentile_thresholds[0]:
            return MeasurementResult.below_3p()
        else:
            return MeasurementResult.between_3p_5p()
