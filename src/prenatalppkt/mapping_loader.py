"""
mapping_loader.py - Loads HPO mappings from YAML configuration
"""

from pathlib import Path
from typing import Dict, List
import yaml
import logging

from prenatalppkt.measurements.term_bin import TermBin, PercentileRange

logger = logging.getLogger(__name__)


class BiometryMappingLoader:
   """Loads HPO mappings from YAML configuration."""
   
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
           logger.warning(f"Mappings file not found: {path}")
           raise FileNotFoundError(f"Mappings file not found: {path}")
       
       with open(path, "r") as f:
           raw_mappings = yaml.safe_load(f)
       
       processed: Dict[str, List[TermBin]] = {}
       
       for measurement_type, ranges in raw_mappings.items():
           bins = []
           
           for range_key, config in ranges.items():
               # Parse "(0,3)" -> PercentileRange
               prange = PercentileRange.from_yaml_key(str(range_key))
               
               # Create TermBin
               term_bin = TermBin(
                   range=prange,
                   hpo_id=config["id"],
                   hpo_label=config["label"],
                   normal=config["normal"]
               )
               bins.append(term_bin)
           
           # Sort bins by min percentile for predictable iteration
           bins.sort(key=lambda b: b.range.min_percentile)
           
           processed[measurement_type] = bins
           logger.debug(f"Loaded {len(bins)} bins for {measurement_type}")
       
       return processed