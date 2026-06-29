"""Tests for prenatalppkt.builders.observer_phenopacket."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from google.protobuf.timestamp_pb2 import Timestamp

from prenatalppkt.builders import build_observer_phenopacket


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
        data, hpo_parser, now_ts, accession_id="A184594_U_1_1"
    )

    assert pps[0].id == "a184594-u-1-1-fetus-1"
    assert pps[0].subject.id == "fetus-1"


def test_hpo_id_dedup_keeps_first_occurrence(hpo_parser, now_ts):
    data = _exam([_fetus_full_biometry(1)])

    pps = build_observer_phenopacket(data, hpo_parser, now_ts)

    pp = pps[0]
    ids = [pf.type.id for pf in pp.phenotypic_features]
    assert len(ids) == len(set(ids)), "PhenotypicFeature HPO ids must be unique"
