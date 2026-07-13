"""Tests for prenatalppkt.builders.observer_phenopacket."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from google.protobuf.timestamp_pb2 import Timestamp

from prenatalppkt.builders import build_observer_phenopacket


DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def now_ts() -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(datetime.now(tz=timezone.utc))
    return ts


def _fetus_full_biometry(fetus_number: int) -> dict:
    return {
        "fetus": {"fetus_number": fetus_number},
        "measurements": [
            {
                "label": "HC",
                "value": 17.5,
                "unit_of_measure": "cm",
                "calculated_percentile": 50.0,
                "calculated_ega": 21.5,
            },
            {
                "label": "BPD",
                "value": 6.8,
                "unit_of_measure": "cm",
                "calculated_percentile": 55.0,
                "calculated_ega": 21.5,
            },
            {
                "label": "AC",
                "value": 21.2,
                "unit_of_measure": "cm",
                "calculated_percentile": 48.0,
                "calculated_ega": 21.5,
            },
            {
                "label": "Femur",
                "value": 4.8,
                "unit_of_measure": "cm",
                "calculated_percentile": 52.0,
                "calculated_ega": 21.5,
            },
        ],
    }


def _fetus_t1(fetus_number: int) -> dict:
    return {
        "fetus": {"fetus_number": fetus_number},
        "measurements": [
            {
                "label": "CRL",
                "value": 5.5,
                "unit_of_measure": "cm",
                "calculated_percentile": 50.0,
                "calculated_ega": 12.0,
            }
        ],
    }


def _fetus_unknown(fetus_number: int) -> dict:
    """A fetus carrying no recognised label - classifier returns UNKNOWN."""
    return {
        "fetus": {"fetus_number": fetus_number},
        "measurements": [
            {
                "label": "Cerebellum",
                "value": 2.1,
                "unit_of_measure": "cm",
                "calculated_percentile": 50.0,
            }
        ],
    }


def _exam(fetuses: list[dict]) -> dict:
    return {"exam": {"fetus_count": len(fetuses)}, "fetuses": fetuses}


def test_single_fetus_t2t3_returns_one_phenopacket(hpo_parser, now_ts):
    data = _exam([_fetus_full_biometry(1)])

    pps = build_observer_phenopacket(data, hpo_parser, now_ts)

    assert len(pps) == 1
    pp = pps[0]
    assert pp.subject.id == "fetus-1"
    assert pp.id == "fetus-1"
    hpo_ids = {pf.type.id for pf in pp.phenotypic_features}
    assert hpo_ids  # at least one biometry term
    for pf in pp.phenotypic_features:
        assert pf.description.startswith("Biometry: ")
    assert pp.meta_data.resources[0].namespace_prefix == "HP"


def test_accession_id_prefixes_phenopacket_id(hpo_parser, now_ts):
    data = _exam([_fetus_full_biometry(1)])

    pps = build_observer_phenopacket(
        data, hpo_parser, now_ts, accession_id="A000001_U_1_1"
    )

    assert pps[0].id == "a000001-u-1-1-fetus-1"
    assert pps[0].subject.id == "a000001-preg1-fetus-1"


def test_twin_returns_two_phenopackets(hpo_parser, now_ts):
    data = _exam([_fetus_full_biometry(1), _fetus_t1(2)])

    pps = build_observer_phenopacket(data, hpo_parser, now_ts, accession_id="TWIN")

    assert len(pps) == 2
    assert [pp.subject.id for pp in pps] == ["twin-fetus-1", "twin-fetus-2"]
    assert [pp.id for pp in pps] == ["twin-fetus-1", "twin-fetus-2"]
    # Twin 2 is T1 - should carry CRL-derived bins
    twin2_descriptions = [pf.description for pf in pps[1].phenotypic_features]
    assert any("crown" in d.lower() or "crl" in d.lower() for d in twin2_descriptions)


def test_subject_id_stable_across_exams_in_same_pregnancy(hpo_parser, now_ts):
    data = _exam([_fetus_full_biometry(1)])

    exam_2 = build_observer_phenopacket(
        data, hpo_parser, now_ts, accession_id="B567817-U-1-2"
    )[0]
    exam_3 = build_observer_phenopacket(
        data, hpo_parser, now_ts, accession_id="B567817-U-1-3"
    )[0]

    assert exam_2.subject.id == exam_3.subject.id == "b567817-preg1-fetus-1"
    assert exam_2.id != exam_3.id


def test_subject_id_differs_across_separate_pregnancies(hpo_parser, now_ts):
    data = _exam([_fetus_full_biometry(1)])

    pregnancy_1 = build_observer_phenopacket(
        data, hpo_parser, now_ts, accession_id="B567817-U-1-1"
    )[0]
    pregnancy_2 = build_observer_phenopacket(
        data, hpo_parser, now_ts, accession_id="B567817-U-2-1"
    )[0]

    assert pregnancy_1.subject.id == "b567817-preg1-fetus-1"
    assert pregnancy_2.subject.id == "b567817-preg2-fetus-1"
    assert pregnancy_1.subject.id != pregnancy_2.subject.id


def test_unknown_fetus_returns_empty_features_phenopacket(hpo_parser, now_ts):
    data = _exam([_fetus_unknown(1)])

    pps = build_observer_phenopacket(data, hpo_parser, now_ts)

    assert len(pps) == 1
    assert list(pps[0].phenotypic_features) == []


def test_hpo_id_dedup_keeps_first_occurrence(hpo_parser, now_ts):
    data = _exam([_fetus_full_biometry(1)])

    pps = build_observer_phenopacket(data, hpo_parser, now_ts)

    pp = pps[0]
    ids = [pf.type.id for pf in pp.phenotypic_features]
    assert len(ids) == len(set(ids)), "PhenotypicFeature HPO ids must be unique"


def test_apple_sally_real_fixture_smoke(hpo_parser, now_ts):
    """End-to-end on a real Observer JSON fixture (single fetus, T2/T3)."""
    raw = json.loads((DATA_DIR / "Apple_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(raw, hpo_parser, now_ts, accession_id="applesally")

    assert len(pps) == 1
    pp = pps[0]
    assert pp.id == "applesally-fetus-1"
    assert pp.subject.id == "applesally-fetus-1"
    assert pp.phenotypic_features  # has at least one term
    for pf in pp.phenotypic_features:
        assert pf.type.id.startswith("HP:")
