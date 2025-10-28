"""
term_bin.py - Core data structures for percentile-to-HPO mapping
"""

from dataclasses import dataclass


@dataclass
class PercentileRange:
   """
   Represents a percentile range with min/max boundaries.
   
   Example:
       >>> prange = PercentileRange(3, 5)
       >>> prange.contains(4.3)
       True
   """
   min_percentile: float
   max_percentile: float
   
   def contains(self, percentile: float) -> bool:
       """Check if percentile falls within this range."""
       return self.min_percentile <= percentile < self.max_percentile
   
   @staticmethod
   def from_yaml_key(key: str) -> "PercentileRange":
       """
       Parse YAML key format into PercentileRange.
       
       Examples:
           "(0,3)" -> PercentileRange(0, 3)
           "(10,50)" -> PercentileRange(10, 50)
       """
       # Remove parentheses and whitespace, then split
       clean = key.strip().strip("()").split(",")
       min_p = float(clean[0].strip())
       max_p = float(clean[1].strip())
       return PercentileRange(min_p, max_p)
   
   def __str__(self) -> str:
       return f"({self.min_percentile},{self.max_percentile})"


@dataclass
class TermBin:
   """
   HPO term mapped to a percentile range.
   
   Example:
       >>> prange = PercentileRange(3, 5)
       >>> bin = TermBin(
       ...     range=prange,
       ...     hpo_id="HP:0040195",
       ...     hpo_label="Decreased head circumference",
       ...     normal=False
       ... )
       >>> bin.fits(4.3)
       True
   """
   range: PercentileRange
   hpo_id: str
   hpo_label: str
   normal: bool
   
   def fits(self, percentile: float) -> bool:
       """Check if a percentile value belongs to this bin."""
       return self.range.contains(percentile)
   
   @property
   def category(self) -> str:
       """
       Derive category from range boundaries.
       
       Returns standard terminology:
       - 0-3: lower_extreme_term
       - 3-5: lower_term
       - 5-10: abnormal_term
       - 10-90: normal_term
       - 90-95: abnormal_term
       - 95-97: upper_term
       - 97-100: upper_extreme_term
       """
       r = self.range
       if r.max_percentile <= 3:
           return "lower_extreme_term"
       elif r.max_percentile <= 5:
           return "lower_term"
       elif r.max_percentile <= 10:
           return "abnormal_term"
       elif r.max_percentile <= 90:
           return "normal_term"
       elif r.max_percentile <= 95:
           return "abnormal_term"
       elif r.max_percentile <= 97:
           return "upper_term"
       else:
           return "upper_extreme_term"