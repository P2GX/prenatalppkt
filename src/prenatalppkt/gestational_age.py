import typing
import math


class GestationalAge:
    """
    A class representing gestational age, expressed in weeks and days.

    Gestational age, defined as the time elapsed since the first day of the last menstrual period (LMP), is typically used in obstetrics to describe the age of an embryo or fetus.
    It is expressed as the number of completed weeks and additional days since the first day of the last menstrual period (LMP). Example 34w3d

    Attributes
    ----------
    _weeks : int
        The number of completed gestational weeks.
    _days : int
        The number of additional days beyond the completed weeks (0-6).

    Methods
    -------
    from_weeks(weeks: Union[int, float]) -> "GestationalAge"
        Create a GestationalAge instance from a numeric week value, which may be an integer or float.
    weeks -> int
        Return the number of completed weeks.
    days -> int
        Return the number of additional days.
    """

    _weeks: int
    _days: int

    def __init__(self, weeks: int, days: int) -> None:
        """
        Initialize a GestationalAge instance.

        Parameters
        ----------
        weeks : int
            The number of completed weeks.
        days : int
            The number of additional days (0-6).
        """
        self._weeks = weeks
        self._days = days

    @staticmethod
    def from_weeks(weeks: typing.Union[int, float]) -> "GestationalAge":
        """
        Construct a GestationalAge object from a numeric week value.

        If `weeks` is an integer, the result will represent that many whole weeks and 0 days.
        If `weeks` is a float, the fractional part will be converted into days.

        Examples
        --------
        >>> GestationalAge.from_weeks(12)
        <GestationalAge: 12 weeks, 0 days>
        >>> GestationalAge.from_weeks(12.5)
        <GestationalAge: 12 weeks, 3 days>

        Parameters
        ----------
        weeks : Union[int, float]
            The gestational age in weeks (can be fractional).

        Returns
        -------
        GestationalAge
            A new instance representing the specified gestational age.
        """
        if isinstance(weeks, int):
            return GestationalAge(weeks=weeks, days=0)
        elif isinstance(weeks, float):
            w = math.floor(weeks)
            week_frac = weeks - w
            d = int(week_frac * 7)
            return GestationalAge(weeks=w, days=d)
        raise TypeError("weeks must be int or float")


    @property
    def weeks(self) -> int:
        """
        Get the number of completed gestational weeks.

        Returns
        -------
        int
            The number of completed weeks.
        """
        return self._weeks

    @property
    def days(self) -> int:
        """
        Get the number of additional gestational days beyond completed weeks.

        Returns
        -------
        int
            The number of days (0-6).
        """
        return self._days
    
    def __repr__(self) -> str:
        return f"GestationalAge(weeks={self._weeks}, days={self._days})"
