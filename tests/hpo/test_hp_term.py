"""Tests for prenatalppkt.hpo.hp_term."""

from __future__ import annotations

import phenopackets.schema.v2 as pps2
import pytest

from prenatalppkt.hpo.hp_term import HpTerm


def _gestational_onset(weeks: int = 20, days: int = 3) -> pps2.TimeElement:
    return pps2.TimeElement(gestational_age=pps2.GestationalAge(weeks=weeks, days=days))


def test_hpterm_accepts_phenopackets_time_element_as_onset():
    onset = _gestational_onset()
    term = HpTerm(hpo_id="HP:0001166", label="Arachnodactyly", onset=onset)
    assert term.onset == onset


def test_set_onset_accepts_phenopackets_time_element():
    term = HpTerm(hpo_id="HP:0001166", label="Arachnodactyly")
    onset = _gestational_onset()
    term.set_onset(onset)
    assert term.onset == onset


def test_set_onset_rejects_non_time_element():
    term = HpTerm(hpo_id="HP:0001166", label="Arachnodactyly")
    with pytest.raises(ValueError):
        term.set_onset("20w3d")
