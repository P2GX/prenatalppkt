# Skeleton for future implementation:
import hpotk
from prenatalppkt.sonographic_measurement import SonographicMeasurement


class FemurLengthMeasurement(SonographicMeasurement):
    """Fetal femur length measurement with HPO term mapping."""

    def __init__(self):
        super().__init__()

        # Define relevant ontology terms
        short_femur = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0003170", name="Short femur", alt_term_ids=[], is_obsolete=False
        )
        decreased_femur_length = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0006464",
            name="Decreased femur length",
            alt_term_ids=[],
            is_obsolete=False,
        )
        abnormal_femur_length = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0006380",
            name="Abnormal femur morphology",
            alt_term_ids=[],
            is_obsolete=False,
        )
        normal_femur = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0001507",
            name="Normal body morphology",
            alt_term_ids=[],
            is_obsolete=False,
        )
        increased_femur_length = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:9999999",
            name="Increased femur length",
            alt_term_ids=[],
            is_obsolete=False,
        )
        long_femur = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:9999998", name="Long femur", alt_term_ids=[], is_obsolete=False
        )

        # Configure mapping using the unified helper
        self.configure_terms(
            lower_extreme_term=short_femur,
            lower_term=decreased_femur_length,
            abnormal_term=abnormal_femur_length,
            normal_term=normal_femur,
            upper_term=increased_femur_length,
            upper_extreme_term=long_femur,
        )

    def name(self) -> str:
        """
        Write the biometric name
        """
        return "femur length"
