from abc import ABC, abstractmethod
from hpotk import MinimalTerm
from prenatalppkt.term_observation import TermObservation
from prenatalppkt.gestational_age import GestationalAge


class SonographicMeasurement(ABC):
    """
    Abstract base class for fetal biometric (sonographic) measurements.

    Provides a framework for:
      o Mapping percentile bins to ontology terms (HPO).
      o Evaluating measurements against a gestational-age-specific
        reference range.
      o Returning standardized `TermObservation` objects.

    Subclasses (e.g., BiparietalDiameterMeasurement, FemurLengthMeasurement)
    should configure which ontology terms correspond to percentile categories
    using either `set_bin_to_term_mapping()` or the simplified
    `configure_terms()` helper.
    """

    _bin_to_term: dict[str, MinimalTerm]

    def __init__(self) -> None:
        """Initialize the base measurement with an empty bin->term mapping."""
        self._bin_to_term = {}

    # ---------------------------------------------------------------------- #
    # Configuration Methods
    # ---------------------------------------------------------------------- #
    def set_bin_to_term_mapping(self, mapping: dict[str, MinimalTerm]) -> None:
        """
        Manually configure the mapping between percentile bins and ontology terms.

        Required keys:
            below_3p, between_3p_5p, between_5p_10p, between_10p_50p,
            between_50p_90p, between_90p_95p, between_95p_97p, above_97p
        """
        required_bins = {
            "below_3p",
            "between_3p_5p",
            "between_5p_10p",
            "between_10p_50p",
            "between_50p_90p",
            "between_90p_95p",
            "between_95p_97p",
            "above_97p",
        }
        missing = required_bins - set(mapping.keys())
        if missing:
            raise ValueError(f"Missing required percentile bins: {missing}")

        self._bin_to_term = mapping

    # ---------------------------------------------------------------------- #
    # Generic Term Configuration Helper
    # ---------------------------------------------------------------------- #
    def configure_terms(
        self,
        *,
        lower_extreme_term,
        lower_term,
        abnormal_term,
        normal_term,
        upper_term,
        upper_extreme_term,
    ) -> None:
        """
        Simplified convenience method for configuring standard percentile bins.

        Parameters
        ----------
        lower_extreme_term : MinimalTerm
            Term for <3rd percentile (severe low extreme).
        lower_term : MinimalTerm
            Term for 3rd-5th percentile (mild low finding).
        abnormal_term : MinimalTerm
            Term for 5th-10th and 90th-95th percentiles (abnormal zone).
        normal_term : MinimalTerm
            Term for 10th-90th percentile range (normal findings).
        upper_term : MinimalTerm
            Term for 95th-97th percentile (mild high finding).
        upper_extreme_term : MinimalTerm
            Term for >97th percentile (severe high extreme).

        Example
        -------
        self.configure_terms(
            lower_extreme_term=microcephaly,
            lower_term=decreased_head_circumference,
            abnormal_term=abnormal_skull_size,
            normal_term=normal_skull_morphology,
            upper_term=increased_head_circumference,
            upper_extreme_term=macrocephaly,
        )
        """
        mapping = {
            "below_3p": lower_extreme_term,
            "between_3p_5p": lower_term,
            "between_5p_10p": abnormal_term,
            "between_10p_50p": normal_term,
            "between_50p_90p": normal_term,
            "between_90p_95p": abnormal_term,
            "between_95p_97p": upper_term,
            "above_97p": upper_extreme_term,
        }
        self.set_bin_to_term_mapping(mapping)

    # ---------------------------------------------------------------------- #
    # Evaluation Logic
    # ---------------------------------------------------------------------- #
    def evaluate(
        self, gestational_age: GestationalAge, measurement_value: float, reference_range
    ) -> TermObservation:
        """
        Evaluate a raw measurement value against the provided reference range
        and map the resulting percentile bin to its configured ontology term.
        """
        # Step 1: compute the percentile bin result
        measurement_result = reference_range.evaluate(measurement_value)

        # Step 2: resolve bin -> term mapping
        bin_key = measurement_result.get_bin_key
        hpo_term = self._bin_to_term.get(bin_key)

        if not hpo_term:
            raise ValueError(f"No HPO term configured for bin '{bin_key}'")

        # Step 3: determine observed flag (abnormal bins only)
        observed = bin_key not in {"between_10p_50p", "between_50p_90p"}

        # Step 4: return standardized TermObservation
        return TermObservation(
            hpo_term=hpo_term, observed=observed, gestational_age=gestational_age
        )

    # ---------------------------------------------------------------------- #
    # Subclasses must define name
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def name(self) -> str:
        """Return the canonical name for this measurement."""
        raise NotImplementedError("Subclasses must implement 'name()'.")
