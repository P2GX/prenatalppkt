import typing

from prenatalppkt.measurements.percentile import Percentile


class MeasurementResult:
    _lower: typing.Optional[Percentile]
    _upper: typing.Optional[Percentile]


    def __init__(self, lower: typing.Optional[Percentile], upper: typing.Optional[Percentile]) -> None:
        self._upper = upper
        self._lower = lower


    @staticmethod
    def below_3p() -> "MeasurementResult":
        return MeasurementResult(lower=None, upper=Percentile.Third)
    

    @staticmethod
    def exactly_3p() -> "MeasurementResult":
        return MeasurementResult(lower=Percentile.Third, upper=Percentile.Third)
    
    @staticmethod
    def between_3p_5p() -> "MeasurementResult":
        return MeasurementResult(lower=Percentile.Third, upper=Percentile.Fifth)
    
