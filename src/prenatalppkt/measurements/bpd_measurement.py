import hpotk
from prenatalppkt.sonographic_measurement import SonographicMeasurement


class BiparietalDiameterMeasurement(SonographicMeasurement):
    """
    Sonographic measurement for Biparietal Diameter (BPD).

    Uses NIHCD and INTERGROWTH percentile references to detect
    skull-size abnormalities. Percentile thresholds are evaluated
    via `ReferenceRange`, and results are mapped to ontology
    (HPO) terms using the standard `configure_terms()` interface.

    Clinical Interpretation
    ------------------------
    - <=5th percentile  -> Microcephaly
    - 5th-10th or 90th-95th percentile -> Abnormality of skull size
    - 10th-90th percentile -> Normal skull morphology
    - >=95th percentile -> Macrocephaly
    """

    def __init__(self):
        super().__init__()

        # Define HPO terms for skull size deviations
        self._microcephaly = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0000252",
            name="Microcephaly",
            alt_term_ids=[],
            is_obsolete=False,
        )
        self._decreased = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0040195",
            name="Decreased head circumference",
            alt_term_ids=[],
            is_obsolete=False,
        )
        self._abnormal = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0000240",
            name="Abnormality of skull size",
            alt_term_ids=[],
            is_obsolete=False,
        )
        self._increased = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0040194",
            name="Increased head circumference",
            alt_term_ids=[],
            is_obsolete=False,
        )
        self._macrocephaly = hpotk.MinimalTerm.create_minimal_term(
            term_id="HP:0000256",
            name="Macrocephaly",
            alt_term_ids=[],
            is_obsolete=False,
        )

        # Configure standardized mapping using the generic helper.
        # Adjusted so <=5th -> Microcephaly, >=95th -> Macrocephaly
        self.configure_terms(
            lower_extreme_term=self._microcephaly,
            lower_term=self._microcephaly,
            abnormal_term=self._abnormal,
            normal_term=None,
            upper_term=self._macrocephaly,
            upper_extreme_term=self._macrocephaly,
        )

    def name(self) -> str:
        """Return the canonical measurement name."""
        return "biparietal diameter"
