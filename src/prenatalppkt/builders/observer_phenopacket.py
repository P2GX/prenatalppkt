"""Observer JSON -> Phenopacket v2 builder.

One Observer JSON file describes one exam with one or more fetuses. This
module stitches `extract_all_fetuses` output together with the exam-level
section parses (impression, anatomy, EFW, pregnancy dating) and returns
one `Phenopacket` per fetus. The caller decides what to do with fetuses
that yielded no phenotypic features (UNKNOWN scan type, missing biometry).
"""

from __future__ import annotations

import re
from typing import Optional

import phenopackets.schema.v2 as pps2
from google.protobuf.timestamp_pb2 import Timestamp

from prenatalppkt.etl.extractors import observer
from prenatalppkt.etl.sections import (
    parse_clinical_impression,
    parse_estimated_fetal_weight,
    parse_fetal_anatomy,
    parse_pregnancy_dating,
)
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.hpo import HpoParser
from prenatalppkt.measurements.term_bin import TermBin


_GA_PATTERN = re.compile(r"at (\d+)w(\d+)d")
_DEFAULT_GA = GestationalAge(weeks=27, days=0)


def _parse_ga_from_description(description: str) -> Optional[tuple[int, int]]:
    m = _GA_PATTERN.search(description or "")
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return None


def _resolve_subject_ga(dating: dict, term_bins: list[TermBin]) -> GestationalAge:
    ga_weeks = dating.get("ga_weeks")
    if ga_weeks:
        return GestationalAge.from_weeks(float(ga_weeks))
    for tb in term_bins:
        parsed = _parse_ga_from_description(tb.description)
        if parsed is not None:
            w, d = parsed
            return GestationalAge(weeks=w, days=d)
    return _DEFAULT_GA


def _biometry_feature(tb: TermBin) -> pps2.PhenotypicFeature:
    parsed = _parse_ga_from_description(tb.description)
    if parsed is not None:
        w, d = parsed
    else:
        w, d = _DEFAULT_GA.weeks, _DEFAULT_GA.days
    return pps2.PhenotypicFeature(
        type=pps2.OntologyClass(id=tb.hpo_id, label=tb.hpo_label),
        excluded=tb.normal,
        description=f"Biometry: {tb.description}",
        onset=pps2.TimeElement(gestational_age=pps2.GestationalAge(weeks=w, days=d)),
    )


def _narrative_feature(
    term, description_prefix: str, subject_ga: GestationalAge
) -> pps2.PhenotypicFeature:
    return pps2.PhenotypicFeature(
        type=pps2.OntologyClass(id=term.hpo_id, label=term.hpo_label),
        description=description_prefix,
        onset=pps2.TimeElement(
            gestational_age=pps2.GestationalAge(
                weeks=subject_ga.weeks, days=subject_ga.days
            )
        ),
    )


def _dedup_by_hpo_id(
    features: list[pps2.PhenotypicFeature],
) -> list[pps2.PhenotypicFeature]:
    seen: set[str] = set()
    out: list[pps2.PhenotypicFeature] = []
    for pf in features:
        if pf.type.id in seen:
            continue
        seen.add(pf.type.id)
        out.append(pf)
    return out


def _hpo_resource(hpo_parser: HpoParser) -> pps2.Resource:
    return pps2.Resource(
        id="hp",
        name="human phenotype ontology",
        url="http://purl.obolibrary.org/obo/hp.owl",
        version=hpo_parser.get_version() or "unknown",
        namespace_prefix="HP",
        iri_prefix="http://purl.obolibrary.org/obo/HP_",
    )


def _phenopacket_id(accession_id: Optional[str], fetus_number: int) -> str:
    if accession_id:
        return f"{accession_id.lower().replace('_', '-')}-fetus-{fetus_number}"
    return f"fetus-{fetus_number}"


def _subject_id(accession_id: Optional[str], fetus_number: int) -> str:
    if accession_id:
        patient = accession_id.lower().replace("_", "-").split("-", 1)[0]
        return f"{patient}-fetus-{fetus_number}"
    return f"fetus-{fetus_number}"


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
    impression = parse_clinical_impression(data, "observer_json", hpo_cr=hpo_cr)
    anatomy = parse_fetal_anatomy(data, "observer_json", hpo_cr=hpo_cr)
    parse_estimated_fetal_weight(data, "observer_json")  # Plan 2 hook

    hp_resource = _hpo_resource(hpo_parser)
    impression_terms = impression.get("hpo_terms", [])
    anatomy_terms = anatomy.get("hpo_terms", [])

    phenopackets: list[pps2.Phenopacket] = []
    for fetus_number, term_bins in bins_by_fetus.items():
        subject_ga = _resolve_subject_ga(dating, term_bins)
        features: list[pps2.PhenotypicFeature] = [
            _biometry_feature(tb) for tb in term_bins
        ]
        for term in impression_terms:
            features.append(
                _narrative_feature(
                    term, f"Clinical impression: {term.hpo_label}", subject_ga
                )
            )
        for term in anatomy_terms:
            features.append(_narrative_feature(term, "Fetal anatomy", subject_ga))
        features = _dedup_by_hpo_id(features)

        pp = pps2.Phenopacket(
            id=_phenopacket_id(accession_id, fetus_number),
            subject=pps2.Individual(
                id=f"fetus-{fetus_number}",
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
