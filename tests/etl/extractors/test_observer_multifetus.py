"""Tests for multi-fetus handling in the Observer JSON extractor.

Real twin exams carry fetuses with different scan types, so extraction runs
per fetus: a CRL/NT-only twin yields T1 bins, a partial/UNKNOWN twin yields [].
"""

from __future__ import annotations

import json
import logging

from prenatalppkt.etl.extractors import observer


def _fetus_full_biometry(fetus_number: int) -> dict:
    """A T2/T3 fetus with the full BPD/HC/AC/Femur biometry set."""
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


def _fetus_t1(fetus_number: int) -> dict:
    """A first-trimester fetus carrying only CRL."""
    return {
        "fetus": {"fetus_number": fetus_number},
        "measurements": [
            {
                "label": "CRL",
                "value": 5.5,
                "unit_of_measure": "cm",
                "calculated_percentile": 50.0,
            }
        ],
    }


def _fetus_partial(fetus_number: int) -> dict:
    """An UNKNOWN fetus: partial biometry, no T1 marker, no full T2/T3 set."""
    return {
        "fetus": {"fetus_number": fetus_number},
        "measurements": [
            {
                "label": "HC",
                "value": 17.5,
                "unit_of_measure": "cm",
                "calculated_percentile": 50.0,
            }
        ],
    }


def test_extract_warns_when_multiple_fetuses_present(caplog):
    """extract() returns only the first fetus's TermBins but warns about the rest."""
    data = {"fetuses": [_fetus_full_biometry(1), _fetus_full_biometry(2)]}

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        term_bins = observer.extract(data)

    assert len(term_bins) == 4
    assert any("2 fetuses" in record.message for record in caplog.records)
    assert any("extract_all_fetuses" in record.message for record in caplog.records)


def test_validate_fetus_count_warns_on_mismatch(caplog):
    """_validate_fetus_count logs a warning when declared count != len(fetuses)."""
    fetuses = [_fetus_full_biometry(1), _fetus_full_biometry(2)]

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        observer._validate_fetus_count(fetuses, declared_count=3)

    assert any("fetus_count=3" in record.message for record in caplog.records)


def test_validate_fetus_count_silent_on_match(caplog):
    """_validate_fetus_count emits no warning when declared count matches."""
    fetuses = [_fetus_full_biometry(1)]

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        observer._validate_fetus_count(fetuses, declared_count=1)

    assert not any("fetus_count" in record.message for record in caplog.records)


def test_validate_fetus_count_silent_when_no_declared_count(caplog):
    """_validate_fetus_count emits no warning when declared count is None."""
    fetuses = [_fetus_full_biometry(1), _fetus_full_biometry(2)]

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        observer._validate_fetus_count(fetuses, declared_count=None)

    assert not any("fetus_count" in record.message for record in caplog.records)


def test_extract_all_fetuses_singleton():
    """Singleton case returns a dict with one key."""
    data = {"exam": {"fetus_count": 1}, "fetuses": [_fetus_full_biometry(1)]}

    result = observer.extract_all_fetuses(data)

    assert set(result.keys()) == {1}
    assert len(result[1]) == 4


def test_extract_all_fetuses_twins():
    """Twins case returns a dict keyed by both fetus_numbers."""
    data = {
        "exam": {"fetus_count": 2},
        "fetuses": [_fetus_full_biometry(1), _fetus_full_biometry(2)],
    }

    result = observer.extract_all_fetuses(data)

    assert set(result.keys()) == {1, 2}
    assert len(result[1]) == 4
    assert len(result[2]) == 4


def test_extract_all_fetuses_discordant_twins():
    """A T1 twin yields its own bins per-fetus; it is NOT emptied.

    Per-fetus scan typing: a CRL-only twin classifies FIRST_TRIMESTER and
    returns one T1 TermBin, while its full-biometry sibling returns four.
    """
    data = {
        "exam": {"fetus_count": 2},
        "fetuses": [_fetus_full_biometry(1), _fetus_t1(2)],
    }

    result = observer.extract_all_fetuses(data)

    assert set(result.keys()) == {1, 2}
    assert len(result[1]) == 4
    assert len(result[2]) == 1


def test_extract_all_fetuses_unknown_twin_is_empty(caplog):
    """An UNKNOWN twin (partial biometry) surfaces as [] without aborting the rest."""
    data = {
        "exam": {"fetus_count": 2},
        "fetuses": [_fetus_full_biometry(1), _fetus_partial(2)],
    }

    with caplog.at_level(
        logging.WARNING, logger="prenatalppkt.etl.extractors.observer"
    ):
        result = observer.extract_all_fetuses(data)

    assert set(result.keys()) == {1, 2}
    assert len(result[1]) == 4
    assert result[2] == []
    assert any("Fetus 2 skipped" in record.message for record in caplog.records)


def test_extract_all_fetuses_from_file(tmp_path):
    """File-loading variant parses JSON and delegates to extract_all_fetuses."""
    data = {
        "exam": {"fetus_count": 2},
        "fetuses": [_fetus_full_biometry(1), _fetus_t1(2)],
    }
    test_file = tmp_path / "twins.json"
    test_file.write_text(json.dumps(data))

    result = observer.extract_all_fetuses_from_file(test_file)

    assert set(result.keys()) == {1, 2}
    assert len(result[1]) == 4
    assert len(result[2]) == 1
