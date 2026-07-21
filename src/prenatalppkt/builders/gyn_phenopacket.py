"""Observer JSON (gyn exam) -> Phenopacket v2 builder.

A gyn exam Observer JSON has no fetuses - the subject is the patient
herself. Structured findings (adnexa/cervix/uterus/uterine_artery/
gyn_procedure/hist_phys_vitals) have no HPO mapping yet (pending
clinical thresholds); only the free-text impression is extracted today,
reusing the same path the fetal builder uses.
"""

from __future__ import annotations

from typing import Optional

import phenopackets.schema.v2 as pps2
from google.protobuf.timestamp_pb2 import Timestamp

from prenatalppkt.etl.sections import parse_clinical_impression
from prenatalppkt.hpo import HpoParser


def _gyn_subject_id(accession_id: Optional[str]) -> str:
    if accession_id:
        return accession_id.lower().replace("_", "-").split("-")[0]
    return "patient"


def _gyn_phenopacket_id(accession_id: Optional[str]) -> str:
    if accession_id:
        return accession_id.lower().replace("_", "-")
    return "gyn-exam"


def _hpo_resource(hpo_parser: HpoParser) -> pps2.Resource:
    return pps2.Resource(
        id="hp",
        name="human phenotype ontology",
        url="http://purl.obolibrary.org/obo/hp.owl",
        version=hpo_parser.get_version() or "unknown",
        namespace_prefix="HP",
        iri_prefix="http://purl.obolibrary.org/obo/HP_",
    )


def _narrative_feature(term) -> pps2.PhenotypicFeature:
    return pps2.PhenotypicFeature(
        type=pps2.OntologyClass(id=term.hpo_id, label=term.hpo_label),
        description="Gyn exam impression",
    )


def build_gyn_phenopacket(
    data: dict,
    hpo_parser: HpoParser,
    created_at: Timestamp,
    *,
    accession_id: Optional[str] = None,
) -> pps2.Phenopacket:
    """Build one Phenopacket for a gyn exam (no fetus).

    Only extracts HPO terms from the free-text impression today
    (`finalize.generalComment.plain_text`, populated on every real gyn
    exam checked). The structured adnexa/cervix/uterus/uterine_artery/
    gyn_procedure/hist_phys_vitals sections have no HPO mapping yet - see
    the TODOs below; each needs a clinical threshold decision (analogous
    to #90a's SGA/LGA gap) before it can be added.

    Args:
        data: Parsed gyn exam Observer JSON dictionary (`fetuses` empty).
        hpo_parser: Loaded HpoParser for the concept recognizer + resource version.
        created_at: Timestamp to stamp into the Phenopacket's MetaData.
        accession_id: Optional exam accession (`<accession>-G-<b>`), used
            for the subject/record ids.

    Returns:
        One Phenopacket for this gyn exam.
    """
    hpo_cr = hpo_parser.get_hpo_concept_recognizer()
    impression = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)
    features = [_narrative_feature(term) for term in impression.get("hpo_terms", [])]

    exam = data.get("exam", {})
    age_years = exam.get("pt_age_at_exam")
    time_at_last_encounter = None
    if age_years:
        time_at_last_encounter = pps2.TimeElement(
            age=pps2.Age(iso8601duration=f"P{int(age_years)}Y")
        )

    # TODO(@VarenyaJ): #92 - the following gyn sections have no HPO
    # mapping yet, pending clinical thresholds from Ron/Michael/Peter
    # (same kind of gap as #90a's SGA/LGA classification):
    # - adnexa: ovary/tube size + Doppler findings (data["adnexa"])
    # - cervix: length, cerclage, funneling (data["cervix"])
    # - uterus: shape, size, position (data["uterus"])
    # - uterine_artery: Doppler indices (data["uterine_artery"])
    # - gyn_procedure: hysteroscopy/sonohysterography findings
    #   (data["gyn_procedure"])
    # - hist_phys_vitals: BP/BMI/vitals (data["hist_phys_vitals"])
    # - exam["ob_gyn_history"]: GPTAL counts - etl/sections/
    #   maternal_history.py's parse_maternal_history() is an
    #   unimplemented skeleton scoped for exactly this; wiring it in is
    #   a separate follow-up, not attempted here.

    return pps2.Phenopacket(
        id=_gyn_phenopacket_id(accession_id),
        subject=pps2.Individual(
            id=_gyn_subject_id(accession_id),
            time_at_last_encounter=time_at_last_encounter,
        ),
        phenotypic_features=features,
        meta_data=pps2.MetaData(
            created=created_at,
            created_by="prenatalppkt",
            resources=[_hpo_resource(hpo_parser)],
            phenopacket_schema_version="2.0",
        ),
    )
