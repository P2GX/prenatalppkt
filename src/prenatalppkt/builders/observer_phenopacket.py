"""Observer JSON -> Phenopacket v2 builder.

One Observer JSON file describes one exam with one or more fetuses. This
module stitches `extract_all_fetuses` output together with the exam-level
section parses (impression, anatomy, EFW, pregnancy dating) and returns
one `Phenopacket` per fetus. The caller decides what to do with fetuses
that yielded no phenotypic features (UNKNOWN scan type, missing biometry).
"""

from __future__ import annotations

import re

from prenatalppkt.gestational_age import GestationalAge


_GA_PATTERN = re.compile(r"at (\d+)w(\d+)d")
_DEFAULT_GA = GestationalAge(weeks=27, days=0)
