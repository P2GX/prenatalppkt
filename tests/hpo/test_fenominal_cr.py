"""Tests for prenatalppkt.hpo.fenominal_cr."""

from __future__ import annotations

import pytest

from prenatalppkt.hpo.fenominal_cr import FenominalConceptRecognizer
from prenatalppkt.hpo.simple_term import SimpleTerm


@pytest.fixture(scope="session")
def fenominal_cr(hp_json_path) -> FenominalConceptRecognizer:
    return FenominalConceptRecognizer(hp_json_path)


def test_parse_returns_simple_terms(fenominal_cr):
    terms = fenominal_cr.parse("Patient presents with severe microcephaly.")
    assert isinstance(terms, list)
    assert all(isinstance(t, SimpleTerm) for t in terms)
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0000252" in by_id
    assert by_id["HP:0000252"].hpo_label == "Microcephaly"
    assert by_id["HP:0000252"].excluded is False


def test_parse_carries_negation_as_excluded(fenominal_cr):
    terms = fenominal_cr.parse("No evidence of microcephaly.")
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0000252" in by_id
    assert by_id["HP:0000252"].excluded is True


def test_parse_coerces_non_string_input(fenominal_cr):
    assert fenominal_cr.parse(123) == []


def test_parse_empty_text_returns_empty(fenominal_cr):
    assert fenominal_cr.parse("") == []
