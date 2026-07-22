"""Tests for prenatalppkt.builders.viewpoint_phenopacket."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from google.protobuf.json_format import MessageToJson, Parse
from google.protobuf.timestamp_pb2 import Timestamp
import phenopackets.schema.v2 as pps2

from prenatalppkt.builders import build_viewpoint_phenopacket


DATA_DIR = Path(__file__).parent.parent / "data"

_SINGLE_FETUS_HL7 = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm&millimeters^mm&millimeters
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%&percent^fmt&formatted
OBX|4|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm&millimeters^mm&millimeters
OBX|5|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%&percent^fmt&formatted
"""


@pytest.fixture
def now_ts() -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(datetime.now(tz=timezone.utc))
    return ts


def test_single_fetus_returns_one_phenopacket(hpo_parser, now_ts):
    pps = build_viewpoint_phenopacket(_SINGLE_FETUS_HL7, hpo_parser, now_ts)

    assert len(pps) == 1
    pp = pps[0]
    assert pp.subject.id == "fetus-1"
    assert pp.id == "fetus-1"
    hpo_ids = {pf.type.id for pf in pp.phenotypic_features}
    assert hpo_ids
    for pf in pp.phenotypic_features:
        assert pf.description.startswith("Biometry: ")
    assert pp.meta_data.resources[0].namespace_prefix == "HP"
    assert pp.meta_data.created_by == "prenatalppkt"


def test_accession_id_prefixes_phenopacket_id(hpo_parser, now_ts):
    pps = build_viewpoint_phenopacket(
        _SINGLE_FETUS_HL7, hpo_parser, now_ts, accession_id="A000001_U_1_1"
    )

    assert pps[0].id == "a000001-u-1-1-fetus-1"
    assert pps[0].subject.id == "a000001-preg1-fetus-1"


def test_no_accession_falls_back(hpo_parser, now_ts):
    pps = build_viewpoint_phenopacket(_SINGLE_FETUS_HL7, hpo_parser, now_ts)

    assert pps[0].id == "fetus-1"
    assert pps[0].subject.id == "fetus-1"


def test_subject_id_stable_across_exams_in_same_pregnancy(hpo_parser, now_ts):
    exam_2 = build_viewpoint_phenopacket(
        _SINGLE_FETUS_HL7, hpo_parser, now_ts, accession_id="B567817-U-1-2"
    )[0]
    exam_3 = build_viewpoint_phenopacket(
        _SINGLE_FETUS_HL7, hpo_parser, now_ts, accession_id="B567817-U-1-3"
    )[0]

    assert exam_2.subject.id == exam_3.subject.id == "b567817-preg1-fetus-1"
    assert exam_2.id != exam_3.id


def test_subject_id_differs_across_separate_pregnancies(hpo_parser, now_ts):
    pregnancy_1 = build_viewpoint_phenopacket(
        _SINGLE_FETUS_HL7, hpo_parser, now_ts, accession_id="B567817-U-1-1"
    )[0]
    pregnancy_2 = build_viewpoint_phenopacket(
        _SINGLE_FETUS_HL7, hpo_parser, now_ts, accession_id="B567817-U-2-1"
    )[0]

    assert pregnancy_1.subject.id == "b567817-preg1-fetus-1"
    assert pregnancy_2.subject.id == "b567817-preg2-fetus-1"
    assert pregnancy_1.subject.id != pregnancy_2.subject.id


def test_hpo_id_dedup_keeps_first_occurrence(hpo_parser, now_ts):
    pps = build_viewpoint_phenopacket(_SINGLE_FETUS_HL7, hpo_parser, now_ts)

    ids = [pf.type.id for pf in pps[0].phenotypic_features]
    assert len(ids) == len(set(ids)), "PhenotypicFeature HPO ids must be unique"


def test_twins_returns_two_phenopackets(hpo_parser, now_ts):
    data = (DATA_DIR / "viewpoint_hl7_twins_test.txt").read_text()

    pps = build_viewpoint_phenopacket(data, hpo_parser, now_ts, accession_id="TWIN")

    assert len(pps) == 2
    assert [pp.subject.id for pp in pps] == ["twin-fetus-1", "twin-fetus-2"]
    assert [pp.id for pp in pps] == ["twin-fetus-1", "twin-fetus-2"]


_TWIN_ANATOMY_HL7 = """
MSH|^~\\&|ViewPoint|Hospital|||20260115120000||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm&millimeters^mm&millimeters
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%&percent^fmt&formatted
OBX|4|ST|BrainFetus.CerebellumAppearance^Cerebellum appearance|Fetus1|abnormal
OBX|5|ST|BrainFetus.CerebellumDetails^Cerebellum details|Fetus1|cerebellar hypoplasia
OBX|6|ST|Fetus.Identifier^Fetus Identifier|Fetus2|B
OBX|7|NM|SkullFetus.HeadCircumference^HC|Fetus2|170^170.0|mm&millimeters^mm&millimeters
OBX|8|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus2|45^45%|%&percent^fmt&formatted
OBX|9|ST|BrainFetus.LateralVentricleLAppearance^Left lateral ventricle appearance|Fetus2|abnormal
OBX|10|ST|BrainFetus.LateralVentricleLDetails^Left lateral ventricle details|Fetus2|ventriculomegaly
"""


def test_twin_each_fetus_keeps_its_own_anatomy_finding(hpo_parser, now_ts):
    """A twin ViewPoint HL7 message's fetuses each carry their own
    anatomy OBX segments (tagged Fetus1/Fetus2, the same sub-id biometry
    segments use) - fetus 2 must not inherit fetus 1's anomaly."""
    pps = build_viewpoint_phenopacket(
        _TWIN_ANATOMY_HL7, hpo_parser, now_ts, accession_id="TWIN"
    )

    assert len(pps) == 2
    fetus1_hpo_ids = {pf.type.id for pf in pps[0].phenotypic_features}
    fetus2_hpo_ids = {pf.type.id for pf in pps[1].phenotypic_features}
    assert "HP:0001321" in fetus1_hpo_ids  # Cerebellar hypoplasia
    assert "HP:0002119" not in fetus1_hpo_ids  # Ventriculomegaly is fetus 2's only
    assert "HP:0002119" in fetus2_hpo_ids  # Ventriculomegaly
    assert "HP:0001321" not in fetus2_hpo_ids  # Cerebellar hypoplasia is fetus 1's only


def test_single_fetus_fixture_complete_findings(hpo_parser, now_ts):
    """viewpoint_hl7_test.txt end-to-end - pure normal biometry, no
    narrative text, so the complete expected HPO set is exactly the
    three core biometry terms, all ruled out (normal readings)."""
    data = (DATA_DIR / "viewpoint_hl7_test.txt").read_text()

    pps = build_viewpoint_phenopacket(data, hpo_parser, now_ts, accession_id="TEST")

    assert len(pps) == 1
    pp = pps[0]
    hpo_ids = {pf.type.id for pf in pp.phenotypic_features}
    assert hpo_ids == {
        "HP:0034207",  # Abnormal fetal gastrointestinal system morphology (AC, normal)
        "HP:0002823",  # Abnormal femur morphology (Femur, normal)
        "HP:0000240",  # Abnormality of skull size (HC, normal)
    }
    assert all(pf.excluded for pf in pp.phenotypic_features)


def test_discrete_hl7_sample_fixture_complete_findings(hpo_parser, now_ts):
    """Discrete_HL7_Messages_Sample.txt end-to-end - a GE ViewPoint
    vendor demo export with joke placeholder patient data (confirmed
    not real PHI), but real-shaped biometry OBX segments. Same shape as
    viewpoint_hl7_test.txt: pure normal biometry, no narrative text."""
    data = (DATA_DIR / "Discrete_HL7_Messages_Sample.txt").read_text()

    pps = build_viewpoint_phenopacket(data, hpo_parser, now_ts, accession_id="DISC")

    assert len(pps) == 1
    pp = pps[0]
    hpo_ids = {pf.type.id for pf in pp.phenotypic_features}
    assert hpo_ids == {
        "HP:0034207",  # Abnormal fetal gastrointestinal system morphology (AC, normal)
        "HP:0002823",  # Abnormal femur morphology (Femur, normal)
        "HP:0000240",  # Abnormality of skull size (HC, normal)
    }
    assert all(pf.excluded for pf in pp.phenotypic_features)


def test_full_exam_fixture_has_biometry_and_anatomy_features(hpo_parser, now_ts):
    """End-to-end on a fixture with both biometry and the 16 anatomy fields.

    HC and BPD share HP:0000240 ("Abnormality of skull size"), so the
    existing HPO-id dedup collapses them to one - the same dedup
    behavior Observer's builder already has, not something new here.
    """
    data = (DATA_DIR / "viewpoint_hl7_full_exam_test.txt").read_text()

    pps = build_viewpoint_phenopacket(
        data, hpo_parser, now_ts, accession_id="FULL00099"
    )

    assert len(pps) == 1
    pp = pps[0]
    descriptions = [pf.description for pf in pp.phenotypic_features]
    assert any(d.startswith("Biometry: ") for d in descriptions)
    assert any(d == "Fetal anatomy" for d in descriptions)
    hpo_ids = {pf.type.id for pf in pp.phenotypic_features}
    assert "HP:0001321" in hpo_ids  # Cerebellar hypoplasia, from the Details field


def test_round_trips_through_message_to_json(hpo_parser, now_ts):
    data = (DATA_DIR / "viewpoint_hl7_full_exam_test.txt").read_text()
    pp = build_viewpoint_phenopacket(
        data, hpo_parser, now_ts, accession_id="FULL00099"
    )[0]

    json_str = MessageToJson(pp)
    round_tripped = Parse(json_str, pps2.Phenopacket())

    assert round_tripped == pp


_NEGATED_FINDING_HL7 = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm&millimeters^mm&millimeters
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%&percent^fmt&formatted
OBX|4|ST|ExamAddData.ExamImpression^Impression|1|The spine was visualized without evidence of a neural tube defect.
"""


def test_negated_narrative_finding_marked_excluded(hpo_parser, now_ts):
    """The HL7 impression text explicitly documents an ABSENT finding
    ("without evidence of a neural tube defect"). fenominal correctly
    flags this SimpleTerm as excluded=True; the resulting
    PhenotypicFeature must carry that same excluded=True rather than
    silently defaulting to "observed/present" - same fix as
    observer_phenopacket.py's identical bug."""
    pps = build_viewpoint_phenopacket(_NEGATED_FINDING_HL7, hpo_parser, now_ts)

    pp = pps[0]
    neural_tube_features = [
        pf for pf in pp.phenotypic_features if pf.type.id == "HP:0045005"
    ]
    assert len(neural_tube_features) == 1
    assert neural_tube_features[0].excluded is True
