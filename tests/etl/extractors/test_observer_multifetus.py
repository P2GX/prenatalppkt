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
