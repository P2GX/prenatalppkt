"""Tests for GestationalAge, in particular from_weeks()'s conversion
from a decimal-week float into whole weeks + days.

This class had zero dedicated tests before this file. That mattered:
the real Observer extractor calls
``GestationalAge.from_weeks(float(ega))`` directly on every raw
gestational-age value it reads, so a bug here silently affects the
gestational age stamped on every biometry finding in the whole
pipeline.
"""

import pytest

from prenatalppkt.gestational_age import GestationalAge


def test_from_weeks_docstring_examples():
    ga = GestationalAge.from_weeks(12)
    assert (ga.weeks, ga.days) == (12, 0)

    ga = GestationalAge.from_weeks(12.5)
    assert (ga.weeks, ga.days) == (12, 3)


@pytest.mark.parametrize("weeks", list(range(10, 43)))
@pytest.mark.parametrize("days", list(range(7)))
def test_from_weeks_round_trips_every_week_and_day_combination(weeks, days):
    """Regression test for a real bug: building the decimal-week value
    the same way the real pipeline does (weeks + days/7, e.g. what a
    source system computing gestational age in days and storing it as
    decimal weeks would produce) and converting it back must recover
    the exact same weeks/days - not silently lose a day.

    Before the fix, 99 of these 231 combinations failed: floating-point
    division/subtraction landed the fraction a hair under the intended
    whole number (e.g. 0.9999999999999964 instead of 1.0), and the old
    int()-based truncation rounded that down to 0 instead of up to 1.
    """
    as_decimal_weeks = weeks + days / 7

    result = GestationalAge.from_weeks(as_decimal_weeks)

    assert (result.weeks, result.days) == (weeks, days)


def test_from_weeks_rejects_non_numeric_input():
    with pytest.raises(TypeError):
        GestationalAge.from_weeks("20.5")  # type: ignore[arg-type]
