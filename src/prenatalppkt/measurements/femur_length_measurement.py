import hpotk
from prenatalppkt.sonographic_measurement import SonographicMeasurement


class FemurLengthMeasurement(SonographicMeasurement):
    """
    Sonographic measurement for fetal Femur Length (FL).

    Uses NIHCD and INTERGROWTH percentile references to evaluate femur length
    relative to gestational age and map percentile categories to relevant
    ontology (HPO) terms.

    Clinical Interpretation
    ------------------------
    - <=3rd percentile       -> Short fetal femur length (HP:0011428)
    - 3rd-5th percentile     -> Short femur (HP:0003097)
    - 5th-10th / 90th-95th   -> Abnormal femur morphology (HP:0002823)
    - 10th-90th percentile   -> Normal range (no HPO term; observed=False)
    - >=95th percentile      -> No HPO term available ("long femur" not in HPO)

    Notes
    -----
    o There are no HPO terms for increased or long femur length.
    o Normal percentile bins are represented as `None` and excluded in downstream
      Phenopacket conversion (`excluded=True`).
    """

    def __init__(self) -> None:
        super().__init__()

        # Define HPO terms for femur length abnormalities
        self._short_fetal_femur = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0011428",
            name="Short fetal femur length",
            alt_term_ids=[],
            is_obsolete=False,
        )
        self._short_femur = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0003097", name="Short femur", alt_term_ids=[], is_obsolete=False
        )
        self._abnormal_femur = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0002823",
            name="Abnormal femur morphology",
            alt_term_ids=[],
            is_obsolete=False,
        )

        # Configure standardized mapping.
        # No upper or "normal" terms are assigned -- those bins will be None.
        self.configure_terms(
            lower_extreme_term=self._short_fetal_femur,
            lower_term=self._short_femur,
            abnormal_term=self._abnormal_femur,
            normal_term=None,
            upper_term=None,
            upper_extreme_term=None,
        )

    def name(self) -> str:
        """Return the canonical measurement name."""
        return "femur length"
