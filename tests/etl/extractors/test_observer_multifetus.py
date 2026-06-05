"""Tests for multi-fetus handling in the Observer JSON extractor."""

from __future__ import annotations

import logging

from prenatalppkt.etl.extractors import observer


def _fetus_with_full_biometry(fetus_number: int) -> dict:
    return {
        "fetus": {"fetus_number": fetus_number},
        "measurements": [
            {
                "label": "HC",
                "value": 17.5,
                "unit_of_measure": "cm",
                "calculated_percentile": 50.0,
            },
            {
                "label": "BPD",
                "value": 6.8,
                "unit_of_measure": "cm",
                "calculated_percentile": 55.0,
            },
            {
                "label": "AC",
                "value": 21.2,
                "unit_of_measure": "cm",
                "calculated_percentile": 48.0,
            },
            {
                "label": "Femur",
                "value": 4.8,
                "unit_of_measure": "cm",
                "calculated_percentile": 52.0,
            },
        ],
    }


def test_extract_warns_when_multiple_fetuses_present(caplog):
    """extract() returns only the first fetus's TermBins but warns about the rest."""
    data = {"fetuses": [_fetus_with_full_biometry(1), _fetus_with_full_biometry(2)]}

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        term_bins = observer.extract(data)

    assert len(term_bins) == 4
    assert any("2 fetuses" in record.message for record in caplog.records)
    assert any("extract_all_fetuses" in record.message for record in caplog.records)


def test_validate_fetus_count_warns_on_mismatch(caplog):
    """_validate_fetus_count logs a warning when declared count != len(fetuses)."""
    fetuses = [_fetus_with_full_biometry(1), _fetus_with_full_biometry(2)]

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        observer._validate_fetus_count(fetuses, declared_count=3)

    assert any("fetus_count=3" in record.message for record in caplog.records)


def test_validate_fetus_count_silent_on_match(caplog):
    """_validate_fetus_count emits no warning when declared count matches."""
    fetuses = [_fetus_with_full_biometry(1)]

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        observer._validate_fetus_count(fetuses, declared_count=1)

    assert not any("fetus_count" in record.message for record in caplog.records)


def test_validate_fetus_count_silent_when_no_declared_count(caplog):
    """_validate_fetus_count emits no warning when declared count is None."""
    fetuses = [_fetus_with_full_biometry(1), _fetus_with_full_biometry(2)]

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        observer._validate_fetus_count(fetuses, declared_count=None)

    assert not any("fetus_count" in record.message for record in caplog.records)


def test_extract_all_fetuses_singleton():
    """Singleton case returns a dict with one key."""
    data = {"exam": {"fetus_count": 1}, "fetuses": [_fetus_with_full_biometry(1)]}

    result = observer.extract_all_fetuses(data)

    assert set(result.keys()) == {1}
    assert len(result[1]) == 4


def test_extract_all_fetuses_twins():
    """Twins case returns a dict keyed by both fetus_numbers."""
    data = {
        "exam": {"fetus_count": 2},
        "fetuses": [_fetus_with_full_biometry(1), _fetus_with_full_biometry(2)],
    }

    result = observer.extract_all_fetuses(data)

    assert set(result.keys()) == {1, 2}
    assert len(result[1]) == 4
    assert len(result[2]) == 4


def test_extract_all_fetuses_discordant_twins(caplog):
    """If one twin is missing biometry, its slot is empty but the other survives."""
    data = {
        "exam": {"fetus_count": 2},
        "fetuses": [
            _fetus_with_full_biometry(1),
            {
                "fetus": {"fetus_number": 2},
                "measurements": [
                    {
                        "label": "CRL",
                        "value": 5.5,
                        "unit_of_measure": "cm",
                        "calculated_percentile": 50.0,
                    }
                ],
            },
        ],
    }

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        result = observer.extract_all_fetuses(data)

    assert set(result.keys()) == {1, 2}
    assert len(result[1]) == 4
    assert result[2] == []
    assert any("Fetus 2 skipped" in record.message for record in caplog.records)
