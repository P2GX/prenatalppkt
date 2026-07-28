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


@pytest.mark.xfail(
    reason=(
        "Known fenominal gap: the exact HPO label 'Dandy-Walker "
        "malformation' returns zero hits, including in total isolation "
        "(not a sentence-context problem). See "
        "test_fetal_anatomy.py's matching xfail for the same gap at "
        "the section-parser level. Remove once fenominal (or a "
        "fallback recognizer) recognizes the phrase."
    ),
    strict=True,
)
def test_parse_recognizes_dandy_walker_malformation(fenominal_cr):
    terms = fenominal_cr.parse("Dandy-Walker malformation")
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0001305" in by_id


@pytest.mark.xfail(
    reason=(
        "Known fenominal gap: negation scope leaks on multi-item "
        "comma/'or' lists. Given 'no evidence of macrocephaly, "
        "ventriculomegaly or agenesis of the corpus callosum' (one "
        "clause negating three findings), fenominal correctly excludes "
        "the first two but not the third, despite identical "
        "grammatical scope. Reproduced on the isolated clause here, "
        "not just the full paragraph, so it's a real parsing behavior, "
        "not sentence-context noise. Remove once fenominal (or a "
        "fallback recognizer) handles multi-item negated lists "
        "correctly."
    ),
    strict=True,
)
def test_parse_negation_scope_covers_full_list(fenominal_cr):
    terms = fenominal_cr.parse(
        "There was no evidence of macrocephaly, ventriculomegaly or "
        "agenesis of the corpus callosum."
    )
    by_id = {t.hpo_id: t for t in terms}
    assert by_id["HP:0000256"].excluded is True  # Macrocephaly
    assert by_id["HP:0002119"].excluded is True  # Ventriculomegaly
    assert by_id["HP:0001274"].excluded is True  # Agenesis of corpus callosum
