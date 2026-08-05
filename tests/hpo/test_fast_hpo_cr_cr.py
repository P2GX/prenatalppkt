"""Tests for prenatalppkt.hpo.fast_hpo_cr_cr.

Skips entirely if the optional fast_hpo_cr extra isn't installed (the
default case - fast_hpo_cr is never installed by default). If it is
installed, the first run pays a real, one-time index-build cost
(observed ~19 minutes against a real hp.obo, not the ~3 minutes its own
README claims); every run after that reuses the on-disk cache and is
fast, same as any other test run.
"""

from __future__ import annotations

import pytest

pytest.importorskip("FastHPOCR")

from prenatalppkt.hpo.fast_hpo_cr_cr import FastHpoCrConceptRecognizer  # noqa: E402
from prenatalppkt.hpo.simple_term import SimpleTerm  # noqa: E402


@pytest.fixture(scope="session")
def fast_hpo_cr_cr() -> FastHpoCrConceptRecognizer:
    return FastHpoCrConceptRecognizer()


def test_parse_returns_simple_terms(fast_hpo_cr_cr):
    terms = fast_hpo_cr_cr.parse("Patient presents with severe microcephaly.")
    assert isinstance(terms, list)
    assert all(isinstance(t, SimpleTerm) for t in terms)
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0000252" in by_id
    assert by_id["HP:0000252"].hpo_label == "Microcephaly"


def test_parse_never_excludes_anything(fast_hpo_cr_cr):
    # fast_hpo_cr has no negation detection at all (confirmed via a
    # full-source grep this session) - excluded must always be False,
    # even for text that plainly negates the finding. This locks in the
    # known limitation as expected behavior, not a bug to chase.
    terms = fast_hpo_cr_cr.parse("No evidence of microcephaly.")
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0000252" in by_id
    assert by_id["HP:0000252"].excluded is False


def test_parse_coerces_non_string_input(fast_hpo_cr_cr):
    assert fast_hpo_cr_cr.parse(123) == []


def test_parse_empty_text_returns_empty(fast_hpo_cr_cr):
    assert fast_hpo_cr_cr.parse("") == []


def test_parse_recognizes_dandy_walker_malformation(fast_hpo_cr_cr):
    # fenominal has a known gap here (see test_fenominal_cr.py's xfail
    # of the same name) - fast_hpo_cr recognizes it directly, verified
    # live this session, so this asserts real behavior, not an xfail.
    terms = fast_hpo_cr_cr.parse("Dandy-Walker malformation")
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0001305" in by_id
