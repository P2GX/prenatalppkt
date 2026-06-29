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
