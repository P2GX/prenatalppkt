"""Tests for prenatalppkt.hpo.composite_cr."""

from __future__ import annotations

import typing

import pytest

from prenatalppkt.hpo.composite_cr import CompositeConceptRecognizer
from prenatalppkt.hpo.ferrific_cr import FerrificConceptRecognizer
from prenatalppkt.hpo.fenominal_cr import FenominalConceptRecognizer
from prenatalppkt.hpo.hpo_cr import HpoConceptRecognizer
from prenatalppkt.hpo.simple_term import SimpleTerm


class _StubRecognizer(HpoConceptRecognizer):
    """A fake recognizer that always returns a fixed list of terms."""

    def __init__(self, terms: typing.List[SimpleTerm]) -> None:
        self._terms = terms
        self.calls: typing.List[str] = []

    def parse(self, cell_contents, custom_d=None) -> typing.List[SimpleTerm]:
        self.calls.append(str(cell_contents))
        return list(self._terms)


def _term(hpo_id: str, label: str) -> SimpleTerm:
    return SimpleTerm(hpo_id=hpo_id, hpo_label=label)


def test_requires_at_least_one_recognizer():
    with pytest.raises(ValueError):
        CompositeConceptRecognizer([])


def test_single_recognizer_passthrough():
    stub = _StubRecognizer([_term("HP:0000252", "Microcephaly")])
    composite = CompositeConceptRecognizer([stub])
    result = composite.parse("some text")
    assert [t.hpo_id for t in result] == ["HP:0000252"]


def test_first_recognizer_wins_when_it_returns_hits():
    first = _StubRecognizer([_term("HP:0000252", "Microcephaly")])
    second = _StubRecognizer([_term("HP:0001305", "Dandy-Walker malformation")])
    composite = CompositeConceptRecognizer([first, second])

    result = composite.parse("some text")

    assert [t.hpo_id for t in result] == ["HP:0000252"]
    assert first.calls == ["some text"]
    assert second.calls == [], (
        "second recognizer should never run - first already had hits"
    )


def test_falls_through_to_next_recognizer_on_zero_hits():
    first = _StubRecognizer([])
    second = _StubRecognizer([_term("HP:0001305", "Dandy-Walker malformation")])
    composite = CompositeConceptRecognizer([first, second])

    result = composite.parse("some text")

    assert [t.hpo_id for t in result] == ["HP:0001305"]
    assert first.calls == ["some text"]
    assert second.calls == ["some text"]


def test_returns_empty_when_every_recognizer_returns_nothing():
    first = _StubRecognizer([])
    second = _StubRecognizer([])
    composite = CompositeConceptRecognizer([first, second])

    assert composite.parse("some text") == []
    assert first.calls == ["some text"]
    assert second.calls == ["some text"]


@pytest.fixture(scope="session")
def fenominal_then_ferrific(hp_json_path) -> CompositeConceptRecognizer:
    # Guards only this fixture, not the whole module - the stub-based
    # tests above never touch ferrific and must keep running even when
    # it isn't installed (the default case in a clean CI install).
    # TODO(@VarenyaJ): same shared-conftest consolidation note as test_ferrific_cr.py.
    pytest.importorskip("ferrific")
    return CompositeConceptRecognizer(
        [
            FenominalConceptRecognizer(hp_json_path),
            FerrificConceptRecognizer(hp_json_path),
        ]
    )


def test_real_chain_falls_back_to_ferrific_on_fenominal_gap(fenominal_then_ferrific):
    # fenominal alone returns zero hits for this exact phrase (see
    # test_fenominal_cr.py's xfail of the same name) - the chain should
    # fall through to ferrific, which recognizes it directly.
    terms = fenominal_then_ferrific.parse("Dandy-Walker malformation")
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0001305" in by_id


def test_real_chain_uses_fenominal_when_it_already_has_hits(fenominal_then_ferrific):
    terms = fenominal_then_ferrific.parse("Patient presents with severe microcephaly.")
    by_id = {t.hpo_id: t for t in terms}
    assert "HP:0000252" in by_id
