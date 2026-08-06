"""Tests for prenatalppkt.hpo.hpo_parser."""

from __future__ import annotations

import shutil
import subprocess
import sys

import pytest

from prenatalppkt.hpo.composite_cr import CompositeConceptRecognizer
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


def test_explicit_fenominal_selection_matches_the_default(hp_json_path):
    parser = HpoParser(hpo_json_file=hp_json_path, concept_recognizer="fenominal")
    assert isinstance(parser.get_hpo_concept_recognizer(), FenominalConceptRecognizer)


def test_single_item_sequence_skips_the_composite_wrapper(hp_json_path):
    # A one-element list is equivalent to passing the bare name - no reason to
    # pay for a CompositeConceptRecognizer wrapper around a single engine.
    parser = HpoParser(hpo_json_file=hp_json_path, concept_recognizer=["fenominal"])
    assert isinstance(parser.get_hpo_concept_recognizer(), FenominalConceptRecognizer)


def test_ferrific_selection_builds_a_ferrific_recognizer(hp_json_path):
    pytest.importorskip("ferrific")
    from prenatalppkt.hpo.ferrific_cr import FerrificConceptRecognizer

    parser = HpoParser(hpo_json_file=hp_json_path, concept_recognizer="ferrific")
    assert isinstance(parser.get_hpo_concept_recognizer(), FerrificConceptRecognizer)


def test_fast_hpo_cr_selection_builds_a_fast_hpo_cr_recognizer(hp_json_path):
    # Skips entirely if the optional fast_hpo_cr extra isn't installed. If it
    # is, and this is the very first use of it in this environment, this pays
    # the real one-time index-build cost (see test_fast_hpo_cr_cr.py's module
    # docstring) - same cost that test file already accepts, not new here.
    pytest.importorskip("FastHPOCR")
    from prenatalppkt.hpo.fast_hpo_cr_cr import FastHpoCrConceptRecognizer

    parser = HpoParser(hpo_json_file=hp_json_path, concept_recognizer="fast_hpo_cr")
    assert isinstance(parser.get_hpo_concept_recognizer(), FastHpoCrConceptRecognizer)


def test_multi_name_chain_builds_a_composite_recognizer(hp_json_path):
    pytest.importorskip("ferrific")
    parser = HpoParser(
        hpo_json_file=hp_json_path, concept_recognizer=["fenominal", "ferrific"]
    )
    assert isinstance(parser.get_hpo_concept_recognizer(), CompositeConceptRecognizer)


def test_fenominal_alone_misses_a_real_gap(hp_json_path):
    # Negative control for the next test: proves the gap is real (fenominal
    # alone really does miss this phrase - see test_fenominal_cr.py's xfail
    # of the same name), not just that the chain happens to also find it
    # independently of whether fenominal actually failed.
    parser = HpoParser(hpo_json_file=hp_json_path, concept_recognizer="fenominal")
    terms = parser.get_hpo_concept_recognizer().parse("Dandy-Walker malformation")
    assert not any(t.hpo_id == "HP:0001305" for t in terms)


def test_composite_chain_closes_the_gap_fenominal_alone_misses(hp_json_path):
    # Real end-to-end proof that concept_recognizer changes actual recognition
    # behavior, not just that it constructs an instance of the right class.
    pytest.importorskip("ferrific")
    parser = HpoParser(
        hpo_json_file=hp_json_path, concept_recognizer=["fenominal", "ferrific"]
    )
    terms = parser.get_hpo_concept_recognizer().parse("Dandy-Walker malformation")
    assert any(t.hpo_id == "HP:0001305" for t in terms)


def test_unknown_name_raises_with_valid_choices_listed(hp_json_path):
    with pytest.raises(ValueError) as exc_info:
        HpoParser(hpo_json_file=hp_json_path, concept_recognizer="not_a_real_engine")
    message = str(exc_info.value)
    assert "not_a_real_engine" in message
    for name in ("fenominal", "ferrific", "fast_hpo_cr"):
        assert name in message


def test_name_matching_is_case_sensitive(hp_json_path):
    with pytest.raises(ValueError, match="unknown concept_recognizer"):
        HpoParser(hpo_json_file=hp_json_path, concept_recognizer="Fenominal")


def test_duplicate_names_raise(hp_json_path):
    with pytest.raises(ValueError, match="duplicate"):
        HpoParser(
            hpo_json_file=hp_json_path, concept_recognizer=["fenominal", "fenominal"]
        )


def test_empty_sequence_raises(hp_json_path):
    with pytest.raises(ValueError, match="at least one recognizer"):
        HpoParser(hpo_json_file=hp_json_path, concept_recognizer=[])


def test_selecting_fenominal_never_imports_the_other_engines(hp_json_path):
    # Runs in a fresh subprocess so sys.modules starts empty - a same-process
    # check would give a false pass if an earlier test in this same pytest
    # run already imported ferrific/FastHPOCR for its own, unrelated
    # importorskip-gated tests.
    code = (
        "import sys\n"
        "from prenatalppkt.hpo.hpo_parser import HpoParser\n"
        f"HpoParser(hpo_json_file={hp_json_path!r}, concept_recognizer='fenominal')\n"
        "assert 'ferrific' not in sys.modules, 'ferrific should not be imported'\n"
        "assert 'FastHPOCR' not in sys.modules, 'FastHPOCR should not be imported'\n"
        "print('OK')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"
    assert result.stdout.strip() == "OK"
