"""Tests for prenatalppkt.hpo.hpo_parser."""

from __future__ import annotations

import shutil

from prenatalppkt.hpo.fenominal_cr import FenominalConceptRecognizer
from prenatalppkt.hpo.hpo_parser import HpoParser


def test_get_hpo_concept_recognizer_returns_fenominal(hpo_parser: HpoParser):
    cr = hpo_parser.get_hpo_concept_recognizer()
    assert isinstance(cr, FenominalConceptRecognizer)
    terms = cr.parse("Patient presents with severe microcephaly.")
    assert any(t.hpo_id == "HP:0000252" for t in terms)


def test_recognizer_survives_hp_json_deletion(hp_json_path, tmp_path):
    # The recognizer is built in __init__, so a caller can delete the hp.json
    # file right after and still use it.
    ephemeral = tmp_path / "hp.json"
    shutil.copy(hp_json_path, ephemeral)
    parser = HpoParser(hpo_json_file=str(ephemeral))
    ephemeral.unlink()
    terms = parser.get_hpo_concept_recognizer().parse("severe microcephaly")
    assert any(t.hpo_id == "HP:0000252" for t in terms)
