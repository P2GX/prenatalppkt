"""Tests for the EFW Measurement builder + corpus expectations.

Parallels `tests/test_loinc_workflow_corpus.py` in structure: declarative
expected outputs per fixture so the EFW pipeline's behaviour is encoded as
assertions.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from prenatalppkt.etl.sections import parse_estimated_fetal_weight
from prenatalppkt.measurements.efw_measurement import (
    LOINC_CODE,
    LOINC_LABEL,
    UNIT_CODE,
    UNIT_LABEL,
    build_efw_measurement,
)

DATA_DIR = Path("tests/data")

# Verified by running parse_estimated_fetal_weight() over each fixture;
# pinned here so changes to the EFW parser surface as test diffs.
EXPECTED_EFW_GRAMS = {
    "Apple_Sally_pretty.json": 1014.8,
    "Blue_Sally_pretty.json": 598.2,
    "Charm_Sally_pretty.json": 2778.3,
    "Eclair_Sally_pretty.json": 1273.7,
}


def test_builder_shape():
    """Builder emits the standard Phenopacket v2 Measurement dict."""
    msmt = build_efw_measurement({"efw_grams": 1014.8})

    assert msmt == {
        "assay": {"id": "LOINC:11727-5", "label": "Fetal Body weight estimated by US"},
        "value": {
            "quantity": {"unit": {"id": "UO:0000021", "label": "gram"}, "value": 1014.8}
        },
    }


def test_builder_returns_none_when_efw_is_none():
    assert build_efw_measurement(None) is None


def test_builder_returns_none_when_efw_grams_missing():
    """Empty / missing-grams dict surfaces as None, not a malformed Measurement."""
    assert build_efw_measurement({}) is None
    assert build_efw_measurement({"percentile": 50.0}) is None
    assert build_efw_measurement({"efw_grams": None}) is None


def test_module_constants_match_user_correction():
    """LOINC code is 11727-5 (NOT 11727-3); unit is grams (NOT mm)."""
    assert LOINC_CODE == "LOINC:11727-5"
    assert LOINC_LABEL == "Fetal Body weight estimated by US"
    assert UNIT_CODE == "UO:0000021"
    assert UNIT_LABEL == "gram"


@pytest.mark.parametrize("fixture_name", sorted(EXPECTED_EFW_GRAMS.keys()))
def test_corpus_fixture_yields_efw_measurement(fixture_name):
    """Each T2/T3 fixture produces an EFW Measurement with the expected grams."""
    fixture = DATA_DIR / fixture_name
    if not fixture.exists():
        pytest.skip(f"{fixture_name} not found")

    data = json.loads(fixture.read_text(encoding="utf-8"))
    efw = parse_estimated_fetal_weight(data, "observer_json")
    msmt = build_efw_measurement(efw)

    assert msmt is not None
    assert msmt["assay"]["id"] == "LOINC:11727-5"
    assert msmt["value"]["quantity"]["unit"]["id"] == "UO:0000021"
    assert msmt["value"]["quantity"]["value"] == pytest.approx(
        EXPECTED_EFW_GRAMS[fixture_name], abs=0.1
    )


def test_corpus_diva_first_trimester_has_no_efw():
    """Diva (T1, CRL only) has no EFW; builder returns None on empty parser output."""
    fixture = DATA_DIR / "Diva_Sally_pretty.json"
    if not fixture.exists():
        pytest.skip("Diva_Sally_pretty.json not found")

    data = json.loads(fixture.read_text(encoding="utf-8"))
    efw = parse_estimated_fetal_weight(data, "observer_json")

    # Either the parser returns an empty dict or one with efw_grams=None.
    # Either way, the builder produces no Measurement.
    assert build_efw_measurement(efw) is None
