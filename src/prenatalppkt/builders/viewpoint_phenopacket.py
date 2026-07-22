"""ViewPoint HL7 -> Phenopacket v2 builder.

One ViewPoint HL7 message describes one exam with one or more fetuses.
This module stitches `extract_all_fetuses` output together with the
exam-level section parses (impression, anatomy, pregnancy dating) and
returns one `Phenopacket` per fetus. The caller decides what to do with
fetuses that yielded no phenotypic features.

GA-resolution, feature-construction, dedup, and id-formatting helpers live
in `builders/_shared.py`, shared with the Observer builder.

TODO @VarenyaJ: parse_fetal_anatomy is computed once for the whole
message and applied to every fetus below - unlike the Observer builder
(fixed to read each fetus's own anatomy data), the ViewPoint HL7 anatomy
parser has no per-fetus split yet, so a twin exam's second fetus would
inherit the first fetus's anatomy findings the same way Observer's used
to. Needs HL7 segment-level fetus disambiguation (e.g. by OBR set ID) to
fix properly, not just an index parameter - real work, not done here.
"""

from __future__ import annotations

from typing import Optional

import phenopackets.schema.v2 as pps2
from google.protobuf.timestamp_pb2 import Timestamp

from prenatalppkt.builders._shared import (
    biometry_feature,
    dedup_by_hpo_id,
    hpo_resource,
    narrative_feature,
    phenopacket_id,
    resolve_subject_ga,
    subject_id,
)
from prenatalppkt.etl.extractors import viewpoint_hl7
from prenatalppkt.etl.sections import (
    parse_clinical_impression,
    parse_fetal_anatomy,
    parse_pregnancy_dating,
)
from prenatalppkt.hpo import HpoParser


def build_viewpoint_phenopacket(
    data: str,
    hpo_parser: HpoParser,
    created_at: Timestamp,
    *,
    accession_id: Optional[str] = None,
) -> list[pps2.Phenopacket]:
    """Build one Phenopacket per fetus from a ViewPoint HL7 message string.

    Args:
        data: ViewPoint HL7 message content as string.
        hpo_parser: Loaded HpoParser for the concept recognizer + resource version.
        created_at: Timestamp to stamp into each Phenopacket's MetaData.
        accession_id: Optional exam accession to use as the subject-id prefix.

    Returns:
        One Phenopacket per fetus found in `data`. A fetus whose
        extraction yielded no term bins produces a Phenopacket with no
        phenotypic features so the caller can decide whether to drop it.
    """
    hpo_cr = hpo_parser.get_hpo_concept_recognizer()

    bins_by_fetus = viewpoint_hl7.extract_all_fetuses(data)
    dating = parse_pregnancy_dating(data, "viewpoint_hl7")
    impression = parse_clinical_impression(data, "viewpoint_hl7", hpo_cr=hpo_cr)
    anatomy = parse_fetal_anatomy(data, "viewpoint_hl7", hpo_cr=hpo_cr)

    hp_resource = hpo_resource(hpo_parser)
    impression_terms = impression.get("hpo_terms", [])
    anatomy_terms = anatomy.get("hpo_terms", [])

    phenopackets: list[pps2.Phenopacket] = []
    for fetus_number, term_bins in bins_by_fetus.items():
        subject_ga = resolve_subject_ga(dating, term_bins)
        features: list[pps2.PhenotypicFeature] = [
            biometry_feature(tb) for tb in term_bins
        ]
        for term in impression_terms:
            features.append(
                narrative_feature(
                    term, f"Clinical impression: {term.hpo_label}", subject_ga
                )
            )
        for term in anatomy_terms:
            features.append(narrative_feature(term, "Fetal anatomy", subject_ga))
        features = dedup_by_hpo_id(features)

        pp = pps2.Phenopacket(
            id=phenopacket_id(accession_id, fetus_number),
            subject=pps2.Individual(
                id=subject_id(accession_id, fetus_number),
                time_at_last_encounter=pps2.TimeElement(
                    gestational_age=pps2.GestationalAge(
                        weeks=subject_ga.weeks, days=subject_ga.days
                    )
                ),
            ),
            phenotypic_features=features,
            meta_data=pps2.MetaData(
                created=created_at,
                created_by="prenatalppkt",
                resources=[hp_resource],
                phenopacket_schema_version="2.0",
            ),
        )
        phenopackets.append(pp)

    return phenopackets
