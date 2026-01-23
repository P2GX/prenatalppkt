"""
src/prenatalppkt/dto/fetus/observer/fetus_anatomy_data.py

Anatomy findings and clinical impressions grouping.
"""

from dataclasses import dataclass
from typing import Any, List, Optional
from prenatalppkt.hpo.simple_term import SimpleTerm
from prenatalppkt.dto.observer.fetuses.fetus_impression_data import FetusImpressionData


@dataclass
class FetusAnatomyData:
    """
    Grouped anatomy-related data from Observer JSON.

    Attributes:
        hpo_terms: HPO phenotype terms extracted from anatomy_text
        anatomy_text: Free-text anatomy findings (from fetus.anatomy_text)
        anatomy: Structured anatomy findings array (from fetuses[].anatomy)
        impression: Clinical impressions and anomalies (from fetuses[].impression)
    """

    hpo_terms: List[SimpleTerm]
    anatomy_text: Optional[str] = None
    anatomy: Optional[Any] = None
    impression: Optional[FetusImpressionData] = None

    def __repr__(self) -> str:
        return (
            f"FetusAnatomyData("
            f"hpo_terms={len(self.hpo_terms)}, "
            f"anatomy_text={'present' if self.anatomy_text else 'absent'}, "
            f"anatomy={'present' if self.anatomy else 'absent'}, "
            f"impression={'present' if self.impression else 'absent'})"
        )
