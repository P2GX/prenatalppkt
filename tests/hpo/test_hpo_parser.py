"""Tests for prenatalppkt.hpo.hpo_parser."""

from __future__ import annotations

from prenatalppkt.hpo.fenominal_cr import FenominalConceptRecognizer
from prenatalppkt.hpo.hpo_parser import HpoParser


def test_get_hpo_concept_recognizer_returns_fenominal(hpo_parser: HpoParser):
    cr = hpo_parser.get_hpo_concept_recognizer()
    assert isinstance(cr, FenominalConceptRecognizer)
    terms = cr.parse("Patient presents with severe microcephaly.")
    assert any(t.hpo_id == "HP:0000252" for t in terms)
