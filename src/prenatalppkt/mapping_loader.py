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
        """
        if not path.exists():
            logger.warning("Mappings file not found: %s", path)
            raise FileNotFoundError(f"Mappings file not found: {path}")

        with open(path, encoding="utf-8") as f:
            raw_mappings = yaml.safe_load(f)

        processed: Dict[str, List[TermBin]] = {}

        for measurement_type, range_list in raw_mappings.items():
            bins: List[TermBin] = []

            for range_dict in range_list:
                prange = PercentileRange(
                    min_percentile=float(range_dict["min"]),
                    max_percentile=float(range_dict["max"]),
                )

                term_bin = TermBin(
                    range=prange,
                    hpo_id=range_dict["id"],
                    hpo_label=range_dict["label"],
                    normal=range_dict["normal"],
                )
                bins.append(term_bin)

            bins.sort(key=lambda b: b.range.min_percentile)

            processed[measurement_type] = bins
            logger.debug("Loaded %d bins for %s", len(bins), measurement_type)

        return processed
