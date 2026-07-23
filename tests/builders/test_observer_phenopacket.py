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


def test_twin_each_fetus_keeps_its_own_anatomy_finding(hpo_parser, now_ts):
    """A twin exam's fetuses each carry their own real anatomy data in the
    Observer schema - fetus 2 must not inherit fetus 1's anomaly, and vice
    versa."""
    fetus_1 = _fetus_full_biometry(1)
    fetus_1["anatomy"] = [
        {
            "main": {"label": "Kidney", "anat_state": "Abnormal"},
            "detail": [],
            "anomalies": [{"description": "Renal agenesis"}],
        }
    ]
    fetus_2 = _fetus_full_biometry(2)
    fetus_2["anatomy"] = [
        {
            "main": {"label": "Skull", "anat_state": "Abnormal"},
            "detail": [],
            "anomalies": [{"description": "Acrania"}],
        }
    ]
    data = _exam([fetus_1, fetus_2])

    pps = build_observer_phenopacket(data, hpo_parser, now_ts, accession_id="TWIN")

    assert len(pps) == 2
    fetus1_hpo_ids = {pf.type.id for pf in pps[0].phenotypic_features}
    fetus2_hpo_ids = {pf.type.id for pf in pps[1].phenotypic_features}
    assert "HP:0000104" in fetus1_hpo_ids  # Renal agenesis
    assert "HP:0030716" not in fetus1_hpo_ids  # Acrania belongs to fetus 2 only
    assert "HP:0030716" in fetus2_hpo_ids  # Acrania
    assert "HP:0000104" not in fetus2_hpo_ids  # Renal agenesis belongs to fetus 1 only


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
    """End-to-end on a real Observer JSON fixture (single fetus, T2/T3).

    Checks the complete, specific set of expected findings rather than
    just "produced something" - this is the exact list confirmed by
    hand against the fixture's raw measurements and impression/anatomy
    text. If this list ever needs to change, that's a real behavior
    change worth a human looking at, not just a passing "non-empty"
    check quietly continuing to pass through it."""
    raw = json.loads((DATA_DIR / "Apple_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(raw, hpo_parser, now_ts, accession_id="applesally")

    assert len(pps) == 1
    pp = pps[0]
    assert pp.id == "applesally-fetus-1"
    assert pp.subject.id == "applesally-fetus-1"
    for pf in pp.phenotypic_features:
        assert pf.type.id.startswith("HP:")

    hpo_ids = {pf.type.id for pf in pp.phenotypic_features}
    assert hpo_ids == {
        "HP:0034207",  # Abnormal fetal gastrointestinal system morphology (AC, normal)
        "HP:0000240",  # Abnormality of skull size (BPD/HC, normal)
        "HP:0002823",  # Abnormal femur morphology (Femur, normal)
        "HP:0000256",  # Macrocephaly (clinical impression, ruled out)
        "HP:0002119",  # Ventriculomegaly (clinical impression, ruled out)
        "HP:0001274",  # Agenesis of corpus callosum (clinical impression, present)
        "HP:0045005",  # Neural tube defect (fetal anatomy, ruled out)
    }


@pytest.mark.xfail(
    reason=(
        "Known fenominal gap (see tests/etl/sections/test_fetal_anatomy.py::"
        "test_dandy_walker_malformation_recognized_in_anatomy_text for the "
        "section-parser-level version of this test) threads all the way "
        "through the full builder pipeline: Apple Sally's impression text "
        "names Dandy-Walker malformation exactly, but it never reaches the "
        "final Phenopacket. Remove once fenominal (or "
        "a fallback) recognizes the phrase."
    ),
    strict=True,
)
def test_apple_sally_dandy_walker_reaches_final_phenopacket(hpo_parser, now_ts):
    """Known gap, not a hidden bug: proves the missing finding isn't
    just a section-parser quirk - it's genuinely absent from the final,
    built Phenopacket a real caller would receive."""
    raw = json.loads((DATA_DIR / "Apple_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(raw, hpo_parser, now_ts, accession_id="applesally")

    hpo_ids = {pf.type.id for pf in pps[0].phenotypic_features}
    assert "HP:0001305" in hpo_ids  # Dandy-Walker malformation


def test_blue_sally_real_fixture_complete_findings(hpo_parser, now_ts):
    """Same treatment as Apple: the complete, specific expected HPO set
    for a second real fixture, confirmed by hand against its raw
    measurements and impression/anatomy text."""
    raw = json.loads((DATA_DIR / "Blue_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(raw, hpo_parser, now_ts, accession_id="bluesally")

    assert len(pps) == 1
    hpo_ids = {pf.type.id for pf in pps[0].phenotypic_features}
    assert hpo_ids == {
        "HP:0034207",  # Abnormal fetal gastrointestinal system morphology (AC, normal)
        "HP:0000240",  # Abnormality of skull size (BPD, normal)
        "HP:0002823",  # Abnormal femur morphology (Femur, normal)
        "HP:0000122",  # Unilateral renal agenesis (clinical impression, present)
        "HP:0000813",  # Bicornuate uterus (clinical impression, present)
        "HP:0045005",  # Neural tube defect (fetal anatomy narrative, ruled out)
        "HP:0000104",  # Renal agenesis (fetal anatomy structured anomaly, present)
    }


@pytest.mark.xfail(
    reason=(
        "Known fenominal gap: Blue Sally's impression text says 'possible "
        "unicornuate or bicornuate uterus' - only 'bicornuate' is "
        "recognized. 'unicornuate uterus' tested alone IS recognized as "
        "HP:0031909, so it's specifically the combined sentence that "
        "defeats recognition. Remove once fenominal "
        "(or a fallback) recognizes the phrase in context."
    ),
    strict=True,
)
def test_blue_sally_unicornuate_uterus_reaches_final_phenopacket(hpo_parser, now_ts):
    """Known gap, not a hidden bug."""
    raw = json.loads((DATA_DIR / "Blue_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(raw, hpo_parser, now_ts, accession_id="bluesally")

    hpo_ids = {pf.type.id for pf in pps[0].phenotypic_features}
    assert "HP:0031909" in hpo_ids  # Unicornuate uterus


def test_charm_sally_real_fixture_complete_findings(hpo_parser, now_ts):
    """Same treatment as Apple/Blue: the complete, specific expected HPO
    set for a third real fixture. Charm's BPD is genuinely above the
    97th percentile (a real abnormal biometry reading, not ruled out -
    excluded=False), unlike the other fixtures' normal BPD readings."""
    raw = json.loads((DATA_DIR / "Charm_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(raw, hpo_parser, now_ts, accession_id="charmsally")

    assert len(pps) == 1
    pp = pps[0]
    hpo_ids = {pf.type.id for pf in pp.phenotypic_features}
    assert (
        hpo_ids
        == {
            "HP:0034207",  # Abnormal fetal gastrointestinal system morphology (AC, normal)
            "HP:0000240",  # Abnormality of skull size (BPD, genuinely abnormal - >97th percentile)
            "HP:0002823",  # Abnormal femur morphology (Femur, normal)
            "HP:0010866",  # Abdominal wall defect (clinical impression, present)
            "HP:0001539",  # Omphalocele (clinical impression + fetal anatomy, present)
            "HP:0045005",  # Neural tube defect (fetal anatomy narrative, ruled out)
        }
    )

    skull_feature = next(
        pf for pf in pp.phenotypic_features if pf.type.id == "HP:0000240"
    )
    assert skull_feature.excluded is False  # genuinely abnormal, not ruled out


def test_diva_sally_real_fixture_complete_findings(hpo_parser, now_ts):
    """Same treatment, for the one first-trimester (T1, CRL-only)
    fixture - see the T1-vs-T2/T3 parity TODO for why this one deserves
    its own closer look beyond just this test."""
    raw = json.loads((DATA_DIR / "Diva_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(raw, hpo_parser, now_ts, accession_id="divasally")

    assert len(pps) == 1
    pp = pps[0]
    hpo_ids = {pf.type.id for pf in pp.phenotypic_features}
    assert hpo_ids == {
        "HP:0001511",  # Intrauterine growth retardation (CRL biometry, present)
        "HP:0030716",  # Acrania (clinical impression + fetal anatomy, present)
    }
    # build_observer_phenopacket doesn't populate pp.measurements for any
    # fixture yet (verified: even Apple, whose four core biometries all
    # carry real LOINC codes, produces an empty list too) - a separate,
    # known builder-level gap, not specific to Diva or to CRL's LOINC code.
    assert list(pp.measurements) == []


def test_eclair_sally_real_fixture_complete_findings(hpo_parser, now_ts):
    """Same treatment as Apple/Blue/Charm: the complete, specific
    expected HPO set for a fifth real fixture."""
    raw = json.loads((DATA_DIR / "Eclair_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(
        raw, hpo_parser, now_ts, accession_id="eclairsally"
    )

    assert len(pps) == 1
    hpo_ids = {pf.type.id for pf in pps[0].phenotypic_features}
    assert hpo_ids == {
        "HP:0034207",  # Abnormal fetal gastrointestinal system morphology (AC, normal)
        "HP:0000240",  # Abnormality of skull size (BPD, normal)
        "HP:0002823",  # Abnormal femur morphology (Femur, normal)
        "HP:0001627",  # Abnormal heart morphology (clinical impression, present)
        "HP:0004383",  # Hypoplastic left ventricle (fetal anatomy, present)
    }


@pytest.mark.xfail(
    reason=(
        "Known fenominal gap: Eclair Sally's impression text describes "
        "'a small ascending aorta, and a small but thick-walled left "
        "ventricle and enlarged right heart chambers' - only a generic "
        "'Abnormal heart morphology' parent term survives; the specific "
        "right-heart finding never appears. 'right ventricular "
        "hypertrophy' and 'cardiomegaly' tested alone ARE recognized, so "
        "it's the full-sentence context that defeats recognition, not "
        "missing vocabulary. Remove once fenominal "
        "(or a fallback) recognizes the phrase in context."
    ),
    strict=True,
)
def test_eclair_sally_right_heart_finding_reaches_final_phenopacket(hpo_parser, now_ts):
    """Known gap, not a hidden bug. "Enlarged right heart chambers" is
    clinically an enlarged-heart finding - HP:0001640 Cardiomegaly is
    the single closest match, confirmed recognized when the exact label
    is used in isolation."""
    raw = json.loads((DATA_DIR / "Eclair_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(
        raw, hpo_parser, now_ts, accession_id="eclairsally"
    )

    hpo_ids = {pf.type.id for pf in pps[0].phenotypic_features}
    assert "HP:0001640" in hpo_ids  # Cardiomegaly


def test_negated_narrative_finding_marked_excluded(hpo_parser, now_ts):
    """Apple Sally's anatomy narrative explicitly documents an ABSENT
    finding ("without evidence of a neural tube defect"). fenominal
    correctly flags this SimpleTerm as excluded=True; the resulting
    PhenotypicFeature must carry that same excluded=True rather than
    silently defaulting to "observed/present"."""
    raw = json.loads((DATA_DIR / "Apple_Sally_pretty.json").read_text())

    pps = build_observer_phenopacket(raw, hpo_parser, now_ts)

    pp = pps[0]
    neural_tube_features = [
        pf for pf in pp.phenotypic_features if pf.type.id == "HP:0045005"
    ]
    assert len(neural_tube_features) == 1
    assert neural_tube_features[0].excluded is True
