"""
TermBin factory for creating TermBin objects from biometry measurements.

Handles mapping of measurement names to HPO terms and percentile ranges.
"""

import logging
from typing import List, Optional, Set

from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.percentile_range import PercentileRange
from prenatalppkt.measurements.term_bin import TermBin

logger = logging.getLogger(__name__)

# Enable debug logging by default
logging.basicConfig(level=logging.DEBUG)

# Required measurements that MUST be present in biometry data
REQUIRED_MEASUREMENTS: Set[str] = {"HC", "BPD", "AC", "Femur"}

# Optional measurements (may or may not be present)
OPTIONAL_MEASUREMENTS: Set[str] = {"Nuchal Fold", "Cerebellum", "Humerus", "OFD"}


# TODO(@VarenyaJ): Add HPO mappings for optional measurements
# Current HPO does not have specific terms for:
# - Nuchal Fold thickness abnormalities
# - Cerebellar size abnormalities
# - Humerus length abnormalities
# - OFD (Occipitofrontal Diameter) abnormalities
# These should map to more general skull/bone morphology terms for now


class TermBinFactory:
    """
    Factory for creating TermBin objects from biometry measurements.

    Maps measurement names to appropriate HPO terms based on percentile ranges.
    """

    # HPO term mappings for each measurement type
    # Format: measurement_name -> {range_type -> (hpo_id, hpo_label)}
    _HPO_MAPPINGS = {
        "HC": {
            "increased": ("HP:0000256", "Macrocephaly"),
            "decreased": ("HP:0000252", "Microcephaly"),
            "normal": ("HP:0000240", "Abnormality of skull size"),
        },
        "BPD": {
            "increased": ("HP:0000256", "Macrocephaly"),
            "decreased": ("HP:0000252", "Microcephaly"),
            "normal": ("HP:0000240", "Abnormality of skull size"),
        },
        "AC": {
            "increased": ("HP:0012720", "Abnormal fetal abdominal circumference"),
            "decreased": ("HP:0012720", "Abnormal fetal abdominal circumference"),
            "normal": (
                "HP:0034207",
                "Abnormal fetal gastrointestinal system morphology",
            ),
        },
        "Femur": {
            "increased": ("HP:0003498", "Disproportionate tall stature"),
            "decreased": ("HP:0003498", "Disproportionate short stature"),
            "normal": ("HP:0002823", "Abnormal femur morphology"),
        },
        # TODO(@VarenyaJ): Add mappings for optional measurements when HPO terms available
        # "Nuchal Fold": {...},
        # "Cerebellum": {...},
        # "Humerus": {...},
        # "OFD": {...},
    }

    def create_term_bin(
        self,
        name: str,
        value_mm: float,
        percentile: float,
        gestational_age: Optional[GestationalAge] = None,
        method: Optional[str] = None,
        fetus_number: Optional[int] = None,
    ) -> Optional[TermBin]:
        """
        Create a TermBin from measurement data.

        Args:
            name: Measurement name (e.g., "HC", "BPD")
            value_mm: Measurement value in millimeters
            percentile: Percentile value (0-100 scale)
            gestational_age: Optional gestational age
            method: Optional measurement method (e.g., "Hadlock")
            fetus_number: Optional fetus identifier

        Returns:
            TermBin object or None if measurement cannot be mapped

        Raises:
            ValueError: If percentile is out of valid range or required measurement lacks HPO mapping
        """
        logger.debug(
            f"Creating TermBin: name={name}, value={value_mm}mm, "
            f"percentile={percentile}%, ga={gestational_age}, method={method}"
        )

        # Validate percentile range
        if percentile < 0 or percentile > 100:
            logger.error(f"Invalid percentile for {name}: {percentile}")
            raise ValueError(f"Percentile must be 0-100, got {percentile}")

        # Check for HPO mapping
        mapping = self._HPO_MAPPINGS.get(name)

        if not mapping:
            # Check if this is an optional measurement
            if name in OPTIONAL_MEASUREMENTS:
                logger.warning(
                    f"No HPO mapping for optional measurement '{name}' - skipping. "
                    f"TODO(@VarenyaJ): Add HPO terms when available"
                )
                return None
            else:
                # Required measurement without mapping is an error
                logger.error(f"No HPO mapping for REQUIRED measurement: {name}")
                raise ValueError(
                    f"Missing HPO mapping for required measurement: {name}"
                )

        # Evaluate percentile range
        perc_range = PercentileRange.evaluate(percentile)
        logger.debug(f"Percentile {percentile}% -> range {perc_range.bin_key}")

        # Determine if measurement is normal/abnormal
        is_normal = self._is_normal_range(perc_range)

        # Select appropriate HPO term
        hpo_id, hpo_label = self._select_hpo_term(mapping, perc_range)
        logger.debug(f"Selected HPO: {hpo_id} - {hpo_label}")

        # Build description
        description = self._build_description(
            name, value_mm, percentile, gestational_age, method, fetus_number
        )

        # Create TermBin
        term_bin = TermBin.from_term(
            range=perc_range,
            term_id=hpo_id,
            term_label=hpo_label,
            normal=is_normal,
            description=description,
        )

        logger.debug(f"Created TermBin: {hpo_id} - normal={is_normal}")
        return term_bin

    def _is_normal_range(self, perc_range: PercentileRange) -> bool:
        """Determine if percentile range is considered normal."""
        # Normal range is typically 10th-90th percentile
        normal_bins = {"between_10p_50p", "between_50p_90p"}
        return perc_range.bin_key in normal_bins

    def _select_hpo_term(
        self, mapping: dict, perc_range: PercentileRange
    ) -> tuple[str, str]:
        """
        Select appropriate HPO term based on percentile range.

        Args:
            mapping: HPO mapping dict for this measurement
            perc_range: Evaluated percentile range

        Returns:
            Tuple of (hpo_id, hpo_label)
        """
        # Map percentile ranges to increased/decreased/normal
        if perc_range.bin_key in {"above_97p"}:
            return mapping["increased"]
        elif perc_range.bin_key in {"below_3p"}:
            return mapping["decreased"]
        else:
            return mapping["normal"]

    def _build_description(
        self,
        name: str,
        value_mm: float,
        percentile: float,
        gestational_age: Optional[GestationalAge],
        method: Optional[str],
        fetus_number: Optional[int],
    ) -> str:
        """
        Build human-readable description for TermBin.

        Format: "NAME: value mm (percentile%) at GAw GAd (method) [Fetus N]"
        """
        parts = [f"{name}: {value_mm} mm ({percentile}%)"]

        if gestational_age:
            parts.append(f"at {gestational_age.weeks}w{gestational_age.days}d")

        if method:
            parts.append(f"({method})")

        if fetus_number:
            parts.append(f"[Fetus {fetus_number}]")

        return " ".join(parts)


def validate_required_measurements(term_bins: List[TermBin]) -> None:
    """
    Validate that all required measurements are present.

    Args:
        term_bins: List of created TermBins

    Raises:
        ValueError: If any required measurement is missing
    """
    logger.debug(f"Validating {len(term_bins)} TermBins for required measurements")

    present_measurements = set()
    for tb in term_bins:
        # Description format begins with "NAME: ...", e.g., "HC: 250.0 mm ..."
        name = tb.description.split(":")[0].strip()
        present_measurements.add(name)
        logger.debug(f"Found measurement: {name}")

    logger.debug(f"Present: {present_measurements}")
    logger.debug(f"Required: {REQUIRED_MEASUREMENTS}")

    missing = REQUIRED_MEASUREMENTS - present_measurements

    if missing:
        error_msg = (
            f"Missing required biometry measurements: {', '.join(sorted(missing))}. "
            f"Required measurements are: {', '.join(sorted(REQUIRED_MEASUREMENTS))}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.debug("All required measurements present")
