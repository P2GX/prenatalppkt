"""Tests for prenatalppkt.builders.gyn_phenopacket."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from google.protobuf.timestamp_pb2 import Timestamp

from prenatalppkt.builders import build_gyn_phenopacket
from prenatalppkt.builders.gyn_phenopacket import _gyn_phenopacket_id, _gyn_subject_id

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def now_ts() -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(datetime.now(tz=timezone.utc))
    return ts


def test_gyn_phenopacket_uses_patient_as_subject(hpo_parser, now_ts):
    raw = json.loads((DATA_DIR / "Gwen_Sally_pretty.json").read_text())

    pp = build_gyn_phenopacket(raw, hpo_parser, now_ts, accession_id="GYN00001_G_1")

    assert pp.subject.id == "gyn00001"
    assert pp.subject.time_at_last_encounter.age.iso8601duration == "P41Y"
    assert pp.phenotypic_features
    for pf in pp.phenotypic_features:
        assert pf.type.id.startswith("HP:")


def test_gyn_subject_id_ignores_exam_count():
    assert _gyn_subject_id("A123456_G_2") == "a123456"


def test_gyn_phenopacket_id_has_no_fetus_suffix():
    assert _gyn_phenopacket_id("A123456_G_2") == "a123456-g-2"


def test_gyn_phenopacket_no_accession_falls_back(hpo_parser, now_ts):
    raw = json.loads((DATA_DIR / "Gwen_Sally_pretty.json").read_text())

    pp = build_gyn_phenopacket(raw, hpo_parser, now_ts)

    assert pp.subject.id == "patient"
    assert pp.id == "gyn-exam"
