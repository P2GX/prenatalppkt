"""Loads HPO mappings from YAML configuration."""

from pathlib import Path
from typing import Dict, List
import logging

import yaml

from prenatalppkt.measurements.term_bin import TermBin, PercentileRange

logger = logging.getLogger(__name__)


class BiometryMappingLoader:
    """
    Loads HPO mappings from YAML configuration.

    This class handles all YAML parsing and TermBin construction,
    keeping file I/O separate from measurement evaluation logic.
    """

    @staticmethod
    def load(path: Path) -> Dict[str, List[TermBin]]:
        """
        Load biometry-to-HPO mappings from YAML.

        Args:
            path: Path to biometry_hpo_mappings.yaml

        Returns:
            Dictionary mapping measurement types to lists of TermBins

        Raises:
            FileNotFoundError: If YAML file doesn't exist

        Example:
            >>> mappings = BiometryMappingLoader.load(yaml_path)
            >>> hc_bins = mappings["head_circumference"]
            >>> len(hc_bins)
            8
        """
        if not path.exists():
            logger.warning("Mappings file not found: %s", path)
            raise FileNotFoundError(f"Mappings file not found: {path}")

        with open(path, encoding="utf-8") as f:
            raw_mappings = yaml.safe_load(f)

        processed: Dict[str, List[TermBin]] = {}

        for measurement_type, ranges in raw_mappings.items():
            bins: List[TermBin] = []

            for range_key, config in ranges.items():
                prange = PercentileRange.from_yaml_key(str(range_key))

                term_bin = TermBin(
                    range=prange,
                    hpo_id=config["id"],
                    hpo_label=config["label"],
                    normal=config["normal"],
                )
                bins.append(term_bin)

            bins.sort(key=lambda b: b.range.min_percentile)

            processed[measurement_type] = bins
            logger.debug("Loaded %d bins for %s", len(bins), measurement_type)

        return processed
