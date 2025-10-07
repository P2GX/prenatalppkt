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
    Percentile ranges and HPO mappings:
      - <=3rd percentile       -> Short fetal femur length (HP:0011428)
      - 3rd-5th percentile     -> Short femur (HP:0003097)
      - 5th-10th / 90th-95th   -> Abnormal femur morphology (HP:0002823)
      - 10th-90th percentile   -> Normal range (no HPO term; observed=False)
      - 95th-97th percentile   -> No known phenotype (upper_term=None)
      - >=97th percentile      -> No known phenotype (upper_extreme_term=None)

    Notes
    -----
    o There are no HPO terms for increased or long femur length.
    o Normal and upper percentile bins are represented as `None` and
      handled as `excluded=True` in downstream Phenopacket conversion.
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

        # Configure standardized bin-to-term mapping (mirrors BPD structure)
        # Femur lacks "upper" or "long" HPO terms, so upper bins return None.
        self.configure_terms(
            lower_extreme_term=self._short_fetal_femur,  # <=3rd percentile
            lower_term=self._short_femur,  # 3rd-5th percentile
            abnormal_term=self._abnormal_femur,  # 5th-10th and 90th-95th
            normal_term=None,  # 10th-90th (normal range)
            upper_term=None,  # 95th-97th (no known phenotype)
            upper_extreme_term=None,  # >=97th (no known phenotype)
        )

    def name(self) -> str:
        """Return the canonical measurement name."""
        return "femur length"
