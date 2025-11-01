"""Simple data holder for HPO observations."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from prenatalppkt.gestational_age import GestationalAge


@dataclass
class TermObservation:
    """
    HPO term observation with context.

    Attributes:
        hpo_id: HPO identifier (e.g., "HP:0000252")
        hpo_label: Human-readable label
        category: Category for provenance
        observed: True if abnormality observed, False if excluded
        gestational_age: Gestational age context
        percentile: Original percentile value (for provenance)
    """

    hpo_id: str
    hpo_label: str
    category: str
    observed: bool
    gestational_age: GestationalAge
    percentile: Optional[float] = None

    def to_phenotypic_feature(self) -> Dict[str, object]:
        """
        Convert to Phenopacket phenotypicFeature format.

        Returns:
            Dictionary in Phenopacket v2 format
        """
        feature: Dict[str, object] = {
            "type": {"id": self.hpo_id, "label": self.hpo_label},
            "excluded": not self.observed,
            "onset": {
                "gestationalAge": {
                    "weeks": self.gestational_age.weeks,
                    "days": self.gestational_age.days,
                }
            },
        }

        if self.percentile is not None:
            desc = f"Percentile: {self.percentile:.1f}, Category: {self.category}"
            feature["description"] = desc

        return feature

    def __str__(self) -> str:
        """Return string representation."""
        status = "OBSERVED" if self.observed else "EXCLUDED"
        ga_str = f"{self.gestational_age.weeks}w{self.gestational_age.days}d"
        return f"{status}: {self.hpo_label} ({self.hpo_id}) at {ga_str}"
