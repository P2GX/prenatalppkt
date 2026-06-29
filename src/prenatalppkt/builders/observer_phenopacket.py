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

from prenatalppkt.gestational_age import GestationalAge
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
