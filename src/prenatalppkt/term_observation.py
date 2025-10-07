from dataclasses import dataclass
from typing import Optional
from hpotk import MinimalTerm
from prenatalppkt.gestational_age import GestationalAge


@dataclass
class TermObservation:
    """
    Represents the result of a sonographic measurement relative to an ontology term
    and percentile-based interpretation.

    Attributes
    ----------
    hpo_term : Optional[MinimalTerm]
        The ontology term representing the abnormal finding. None for normal-range measurements.
    observed : bool
        True if the abnormality was observed, False if it was *not* observed (normal finding).
    gestational_age : GestationalAge
        The gestational age context for this observation.
    hpo_id : str
        The ontology identifier (e.g., "HP:0000252").
    hpo_label : str
        The human-readable name of the ontology term (e.g., "Microcephaly").
    """

    hpo_term: Optional[MinimalTerm]
    observed: bool
    gestational_age: GestationalAge
    hpo_id: str = ""
    hpo_label: str = ""

    def __post_init__(self) -> None:
        """
        Automatically populate HPO metadata from MinimalTerm, if available.
        """
        if self.hpo_term is not None and isinstance(self.hpo_term, MinimalTerm):
            if not self.hpo_id:
                self.hpo_id = getattr(self.hpo_term, "term_id", "")
            if not self.hpo_label:
                self.hpo_label = getattr(self.hpo_term, "name", "")
        else:
            # Normal bin or missing ontology concept
            self.hpo_id = ""
            self.hpo_label = ""

    @property
    def excluded(self) -> bool:
        """
        Boolean property following Phenopacket schema:
        True if phenotype was explicitly *not observed* (normal finding).
        """
        return not self.observed

    def to_phenotypic_feature(self) -> dict:
        """
        Serialize this observation to a Phenopacket-like JSON structure.

        Returns
        -------
        dict
            Dictionary representation of a GA4GH PhenotypicFeature message.
        """
        if self.hpo_term is None:
            # For normal findings, omit the `type` but mark `excluded=true`
            return {
                "excluded": True,
                "description": "Normal measurement for gestational age",
            }

        return {
            "type": {"id": self.hpo_id, "label": self.hpo_label},
            "excluded": self.excluded,
            "description": f"Measurement at {self.gestational_age.weeks}w{self.gestational_age.days}d",
        }

    def __repr__(self) -> str:
        """Developer-friendly representation showing label and state."""
        label = self.hpo_label or "None"
        return (
            f"TermObservation(hpo_label='{label}', "
            f"observed={self.observed}, excluded={self.excluded}, "
            f"gestational_age={self.gestational_age.weeks}w{self.gestational_age.days}d)"
        )
