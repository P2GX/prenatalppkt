"""Tests for prenatalppkt.hpo.ferrific_cr.

Skips entirely if the optional ferrific extra isn't installed (the
default case - ferrific is never installed by default), same pattern
as test_fast_hpo_cr_cr.py.

TODO: this per-file importorskip is duplicated across
test_ferrific_cr.py, test_fast_hpo_cr_cr.py, and (per-test) test_hpo_
parser.py/test_composite_cr.py - worth a shared tests/hpo/conftest.py
fixture or marker down the line so a future fourth optional recognizer
doesn't have to rediscover this pattern (or skip it, the way this file
did until CI caught it on a clean install).
"""

from __future__ import annotations

import pytest

pytest.importorskip("ferrific")

from prenatalppkt.hpo.ferrific_cr import FerrificConceptRecognizer  # noqa: E402
from prenatalppkt.hpo.simple_term import SimpleTerm  # noqa: E402


@pytest.fixture(scope="session")
def ferrific_cr(hp_json_path) -> FerrificConceptRecognizer:
    return FerrificConceptRecognizer(hp_json_path)


def test_parse_returns_simple_terms(ferrific_cr):
    terms = ferrific_cr.parse("Patient presents with severe microcephaly.")
    assert isinstance(terms, list)
    assert all(isinstance(t, SimpleTerm) for t in terms)
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0000252" in by_id
    assert by_id["HP:0000252"].hpo_label == "Microcephaly"
    assert by_id["HP:0000252"].excluded is False


def test_parse_carries_negation_as_excluded(ferrific_cr):
    terms = ferrific_cr.parse("No evidence of microcephaly.")
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0000252" in by_id
    assert by_id["HP:0000252"].excluded is True


def test_parse_coerces_non_string_input(ferrific_cr):
    assert ferrific_cr.parse(123) == []


def test_parse_empty_text_returns_empty(ferrific_cr):
    assert ferrific_cr.parse("") == []


def test_parse_recognizes_dandy_walker_malformation(ferrific_cr):
    # fenominal has a known gap here (see test_fenominal_cr.py's xfail
    # of the same name) - ferrific was built specifically to close it,
    # so this asserts real behavior, not an xfail.
    terms = ferrific_cr.parse("Dandy-Walker malformation")
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0001305" in by_id


def test_parse_negation_scope_covers_full_list(ferrific_cr):
    # fenominal leaks negation scope on multi-item comma/"or" lists
    # (see test_fenominal_cr.py's xfail of the same name) - ferrific's
    # clause-scoped negation was built to close this gap.
    terms = ferrific_cr.parse(
        "There was no evidence of macrocephaly, ventriculomegaly or "
        "agenesis of the corpus callosum."
    )
    by_id = {t.hpo_id: t for t in terms}
    assert by_id["HP:0000256"].excluded is True  # Macrocephaly
    assert by_id["HP:0002119"].excluded is True  # Ventriculomegaly
    assert by_id["HP:0001274"].excluded is True  # Agenesis of corpus callosum
