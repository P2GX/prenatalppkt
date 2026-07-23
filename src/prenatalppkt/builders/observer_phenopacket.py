"""Observer JSON -> Phenopacket v2 builder.

One Observer JSON file describes one exam with one or more fetuses. This
module stitches `extract_all_fetuses` output together with the exam-level
section parses (impression, anatomy, EFW, pregnancy dating) and returns
one `Phenopacket` per fetus. The caller decides what to do with fetuses
that yielded no phenotypic features (UNKNOWN scan type, missing biometry).

GA-resolution, feature-construction, dedup, and id-formatting helpers live
in `builders/_shared.py`, shared with the ViewPoint builder.
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
from prenatalppkt.etl.extractors import observer
from prenatalppkt.etl.sections import (
    parse_clinical_impression,
    parse_estimated_fetal_weight,
    parse_fetal_anatomy,
    parse_pregnancy_dating,
)
from prenatalppkt.hpo import HpoParser


def build_observer_phenopacket(
    data: dict,
    hpo_parser: HpoParser,
    created_at: Timestamp,
    *,
    accession_id: Optional[str] = None,
) -> list[pps2.Phenopacket]:
    """Build one Phenopacket per fetus from an Observer JSON dict.

    Args:
        data: Parsed Observer JSON dictionary.
        hpo_parser: Loaded HpoParser for the concept recognizer + resource version.
        created_at: Timestamp to stamp into each Phenopacket's MetaData.
        accession_id: Optional exam accession to use as the subject-id prefix.

    Returns:
        One Phenopacket per fetus in `data["fetuses"]`. A fetus whose
        extraction yielded no term bins (UNKNOWN scan type, or T1 with
        no parseable CRL/NT) produces a Phenopacket with no phenotypic
        features so the caller can decide whether to drop it.
    """
    hpo_cr = hpo_parser.get_hpo_concept_recognizer()

    bins_by_fetus = observer.extract_all_fetuses(data)
    dating = parse_pregnancy_dating(data, "observer_json")
    # Clinical impression (finalize.generalComment) is a single exam-level
    # sign-off note in the Observer schema - there is no per-fetus version
    # to read, so it is computed once and applied to every fetus below.
    impression = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)
    parse_estimated_fetal_weight(data, "observer_json")  # Plan 2 hook
    # TODO(@VarenyaJ): #90a Measurement enrichment (deferred 2026-07-13) -
    # emitting Measurement is unblocked, but turning an abnormal reading
    # into a PhenotypicFeature needs a percentile/z-score threshold from
    # Ron/Michael/Peter, and TermBin only stores a binned PercentileRange
    # (not the raw percentile) while phenopackets' ReferenceRange expects
    # low/high in the same unit as the value (mm) - percentile-as-a-
    # ReferenceRange doesn't map cleanly yet either.

    hp_resource = hpo_resource(hpo_parser)
    impression_terms = impression.get("hpo_terms", [])

    phenopackets: list[pps2.Phenopacket] = []
    for fetus_index, fetus_data in enumerate(data.get("fetuses", [])):
        fetus_number = fetus_data.get("fetus", {}).get("fetus_number", 1)
        term_bins = bins_by_fetus.get(fetus_number, [])
        # Anatomy (structured findings + free-text narrative) is stored per
        # fetus in the Observer schema, so it is read per fetus here too -
        # a twin exam's second fetus must not inherit the first fetus's
        # anatomy findings.
        anatomy = parse_fetal_anatomy(
            data, "observer_json", hpo_cr=hpo_cr, fetus_index=fetus_index
        )
        anatomy_terms = anatomy.get("hpo_terms", [])

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
