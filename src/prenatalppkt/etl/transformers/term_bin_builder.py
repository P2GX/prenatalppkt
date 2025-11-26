"""
TermBin builder for ETL pipeline.

Transforms extracted BiometryCollection into TermBin objects for HPO mapping.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from prenatalppkt.etl.models.biometry import Biometry, BiometryCollection
from prenatalppkt.measurements.percentile_range import PercentileRange
from prenatalppkt.measurements.term_bin import TermBin
from prenatalppkt.mapping_loader import BiometryMappingLoader
from prenatalppkt.hpo.simple_term import SimpleTerm

logger = logging.getLogger(__name__)


class TermBinBuilder:
    """
    Transform BiometryCollection into TermBin objects.

    Uses existing infrastructure:
    - PercentileRange.evaluate() to bin percentiles
    - BiometryMappingLoader to load HPO mappings from YAML
    - TermBin to represent the final mapped observation

    Example usage::

        from prenatalppkt.etl.extractors.observer import ObserverExtractor
        from prenatalppkt.etl.transformers.term_bin_builder import TermBinBuilder

        # Extract biometries
        extractor = ObserverExtractor()
        collection = extractor.extract(data)

        # Transform to term bins
        builder = TermBinBuilder()
        term_bins = builder.build(collection)

        # Use term bins for phenopacket export
        for tb in term_bins:
            print(f"{tb.hpo_label}: {tb.description}")
    """

    def __init__(self, mappings_path: Optional[Path] = None):
        """
        Initialize TermBinBuilder with HPO mappings.

        Args:
            mappings_path: Path to YAML mappings file. If None, uses default.
        """
        # Load HPO mappings using existing infrastructure
        self._mappings: Dict[str, List[TermBin]] = BiometryMappingLoader.load(
            mappings_path or self._get_default_mappings_path()
        )
        logger.info(f"Loaded mappings for {len(self._mappings)} measurement types")

    def build(self, collection: BiometryCollection) -> List[TermBin]:
        """
        Build TermBin objects from BiometryCollection.

        Args:
            collection: Collection of extracted biometry measurements

        Returns:
            List of TermBin objects with HPO mappings
        """
        term_bins = []

        for biometry in collection.measurements:
            term_bin = self._build_single(biometry)
            if term_bin:
                term_bins.append(term_bin)

        logger.info(
            f"Built {len(term_bins)} TermBins from {collection.count} biometries"
        )
        return term_bins

    def _build_single(self, biometry: Biometry) -> Optional[TermBin]:
        """
        Build a single TermBin from a Biometry measurement.

        Args:
            biometry: Single biometry measurement

        Returns:
            TermBin object or None if cannot be mapped
        """
        # Must have percentile to map to TermBin
        if biometry.percentile is None:
            logger.debug(f"Skipping {biometry.name}: no percentile")
            return None

        # Get measurement type for mapping lookup
        measurement_type = self._normalize_measurement_type(biometry.name)

        # Get configured TermBins for this measurement type
        if measurement_type not in self._mappings:
            logger.warning(
                f"No HPO mappings found for measurement type: {measurement_type}"
            )
            return None

        configured_bins = self._mappings[measurement_type]

        # Use PercentileRange.evaluate() to determine which bin this percentile falls into
        target_range = PercentileRange.evaluate(biometry.percentile)

        # Find the TermBin that matches this percentile range
        matching_bin = None
        for tb in configured_bins:
            if tb.range.bin_key == target_range.bin_key:
                matching_bin = tb
                break

        if not matching_bin:
            logger.warning(
                f"No TermBin matches percentile {biometry.percentile} "
                f"({target_range.bin_key}) for {biometry.name}"
            )
            return None

        # Create SimpleTerm from the matched bin
        term = SimpleTerm(hpo_id=matching_bin.hpo_id, hpo_label=matching_bin.hpo_label)

        # Build description from Biometry data
        description = self._build_description(biometry)

        # Use TermBin.from_term() factory method
        return TermBin.from_term(
            range=target_range,
            term=term,
            normal=matching_bin.normal,
            description=description,
        )

    def _build_description(self, biometry: Biometry) -> str:
        """
        Build human-readable description for TermBin.

        Args:
            biometry: Biometry measurement

        Returns:
            Formatted description string like "HC: 233.7 mm (36%) at G25w1d (Hadlock)"
        """
        parts = [
            f"{biometry.name}: {biometry.value_mm} mm",
            f"({biometry.percentile}%)",
        ]

        # gestational_age is now a GestationalAge object
        if biometry.gestational_age:
            ga = biometry.gestational_age
            parts.append(f"at {ga.weeks}w{ga.days}d")

        if biometry.method:
            parts.append(f"({biometry.method})")

        if biometry.fetus_number is not None:
            parts.append(f"[Fetus {biometry.fetus_number}]")

        return " ".join(parts)

    def _normalize_measurement_type(self, name: str) -> str:
        """
        Normalize measurement name to match YAML mapping keys.

        The YAML uses lowercase with underscores (e.g., "head_circumference").
        Our BiometryMeasurement enum uses mixed case (e.g., "HC", "Nuchal Fold").

        Args:
            name: Measurement name from BiometryMeasurement enum

        Returns:
            Normalized name for YAML lookup
        """
        # Map canonical names to YAML keys
        name_map = {
            "HC": "head_circumference",
            "BPD": "biparietal_diameter",
            "AC": "abdominal_circumference",
            "Femur": "femur_length",
            "Nuchal Fold": "nuchal_fold",
            "Cerebellum": "cerebellum",
            "OFD": "occipitofrontal_diameter",
            "Humerus": "humerus_length",
        }

        return name_map.get(name, name.lower().replace(" ", "_"))

    def _get_default_mappings_path(self) -> Path:
        """
        Get path to default HPO mappings YAML.

        Returns:
            Path to biometry_hpo_mappings.yaml
        """
        # Look for mappings at project root in data/mappings/
        # Navigate up from src/prenatalppkt/etl/transformers to project root
        package_root = Path(__file__).parent.parent.parent.parent.parent
        return package_root / "data" / "mappings" / "biometry_hpo_mappings.yaml"
