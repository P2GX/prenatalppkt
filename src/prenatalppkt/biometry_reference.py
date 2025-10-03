"""
biometry_reference.py

Provides access to validated fetal growth reference tables
from NIHCD (NICHD) and INTERGROWTH-21st.

The main entry point is the `FetalGrowthPercentiles` class,
which loads pre-parsed TSV reference tables, supports both
sources, and offers percentile and z-score lookups.

This replaces mock data with structured references that were
parsed from authoritative PDFs and normalized into TSV files.

Data provenance:
- NIHCD: raw_NIHCD_feta_growth_calculator_percentile_range.tsv
- INTERGROWTH-21st: intergrowth21_<measure>_{ct,zs}.tsv
"""

from __future__ import annotations

import logging
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# -----------------------
# Paths and supported measures
# -----------------------

RESOURCES_DIR = Path(__file__).resolve().parents[2] / "data" / "parsed"

# -----------------------
# Supported measures (canonical: long form)
# -----------------------

SUPPORTED_MEASURES = {
    "head_circumference": "Head Circumference",
    "biparietal_diameter": "Biparietal Diameter",
    "abdominal_circumference": "Abdominal Circumference",
    "femur_length": "Femur Length",
    "occipitofrontal_diameter": "Occipito-Frontal Diameter",
}

# Short aliases used only for filenames in Intergrowth-21
SHORT_ALIASES = {
    "head_circumference": "hc",
    "biparietal_diameter": "bpd",
    "abdominal_circumference": "ac",
    "femur_length": "fl",
    "occipitofrontal_diameter": "ofd",
}


# -----------------------
# Column normalization
# -----------------------


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names across sources (GA, percentiles, z-scores)."""
    rename_map = {}
    for col in df.columns:
        c = col.strip().lower()

        # Gestational age column
        if "gest" in c and "week" in c:
            rename_map[col] = "Gestational Age (weeks)"

        # Percentile columns (various formats)
        elif "percentile" in c:
            # e.g. "Percentile 50" -> "50th Percentile"
            num = "".join(ch for ch in c if ch.isdigit())
            if num:
                rename_map[col] = f"{num}th Percentile"
        elif c.startswith("p") and c[1:].isdigit():
            # e.g. "P50" -> "50th Percentile"
            num = c[1:]
            rename_map[col] = f"{num}th Percentile"
        elif c.endswith(("rd", "th", "st")):
            # e.g. "3rd" -> "3rd Percentile"
            num = "".join(ch for ch in c if ch.isdigit())
            if num:
                rename_map[col] = f"{num}th Percentile"

        # Z-score columns
        elif "sd" in c:
            # Normalize e.g. "-2 sd", "+1SD" -> "-2 SD", "1 SD"
            num = "".join(ch for ch in c if ch.isdigit() or ch in "+-")
            if num:
                rename_map[col] = f"{num} SD"

    return df.rename(columns=rename_map)


# -----------------------
# Label parsing helper
# -----------------------


def _extract_numeric_label(label: str) -> float:
    """
    Extract numeric value from a label like '3rd Percentile', '97th Percentile', or '-2 SD'.

    Handles suffixes (st/nd/rd/th) and z-score notation.
    """
    match = re.search(r"-?\d+", label)  # captures integers with optional minus
    if not match:
        raise ValueError(f"Could not extract numeric value from label: {label}")
    return float(match.group(0))


# -----------------------
# Interpolation helper
# -----------------------


def _interpolate_value_to_label(row_values: pd.Series, value_mm: float) -> float:
    """
    Interpolate a measurement value between reference columns.

    Parameters
    ----------
    row_values : pd.Series
        Sorted mapping of column label -> reference value.
    value_mm : float
        Observed measurement value.

    Returns
    -------
    float
        Interpolated label as a float (percentile number or SD value).
    """
    row_values = row_values.sort_values()

    # Boundary conditions: below lowest or above highest centile/z-score
    lowest_label, lowest_val = row_values.index[0], row_values.iloc[0]
    highest_label, highest_val = row_values.index[-1], row_values.iloc[-1]

    if value_mm <= lowest_val:
        return _extract_numeric_label(lowest_label)  # e.g., "3rd Percentile" -> 3
    if value_mm >= highest_val:
        return _extract_numeric_label(highest_label)  # e.g., "97th Percentile" -> 97

    # Interpolate between bounding labels
    items = list(row_values.items())
    for (low_label, low_val), (high_label, high_val) in zip(items, items[1:]):
        if low_val <= value_mm <= high_val:
            low_num = _extract_numeric_label(low_label)
            high_num = _extract_numeric_label(high_label)

            # linear interpolation between bounding columns
            frac = (value_mm - low_val) / (high_val - low_val)
            return low_num + frac * (high_num - low_num)

    # Fallback safety net
    raise ValueError(f"Could not interpolate {value_mm} from given reference row")


# -----------------------
# Main class
# -----------------------


class FetalGrowthPercentiles:
    """
    Load fetal growth percentiles and z-scores for multiple biometrics.

    Attributes
    ----------
    source : str
        "intergrowth" (default) or "nichd".
    tables : Dict[str, pd.DataFrame]
        Dictionary mapping measurement type ("head_circumference", etc.) to parsed DataFrames.
    """

    def __init__(self, source: str = "intergrowth") -> None:
        if source not in {"intergrowth", "nichd"}:
            raise ValueError(
                f"Unsupported source '{source}'. Choose 'intergrowth' or 'nichd'."
            )
        self.source = source
        self.tables: Dict[str, pd.DataFrame] = {}
        self._load_tables()

    # -----------------------
    # Internal helpers
    # -----------------------

    def _load_tables(self) -> None:
        """
        Load all reference tables for the selected source into memory.

        Delegates to either `_load_intergrowth` or `_load_nichd`
        depending on the configured source.
        """
        if self.source == "intergrowth":
            self._load_intergrowth()
        elif self.source == "nichd":
            self._load_nichd()

        logger.debug(
            "Loaded measures for %s: %s", self.source, list(self.tables.keys())
        )

    def _load_intergrowth(self) -> None:
        """
        Load Intergrowth-21st tables for all supported measures.

        Each measure has both centile (ct) and z-score (zs) TSV files,
        which are parsed and stored under `self.tables[long_key]`.
        """
        for long_key, short_key in SHORT_ALIASES.items():
            ct_path = (
                RESOURCES_DIR
                / "intergrowth21_docling_parse"
                / f"intergrowth21_{short_key}_ct.tsv"
            )
            zs_path = (
                RESOURCES_DIR
                / "intergrowth21_docling_parse"
                / f"intergrowth21_{short_key}_zs.tsv"
            )
            if ct_path.exists() and zs_path.exists():
                ct_df = _normalize_columns(pd.read_csv(ct_path, sep="\t"))
                zs_df = _normalize_columns(pd.read_csv(zs_path, sep="\t"))
                self.tables[long_key] = {"ct": ct_df, "zs": zs_df}

    def _load_nichd(self) -> None:
        """
        Load NICHD reference table and split by measurement type.

        NICHD provides one master table with a `Measure` column.
        Each supported measure is matched flexibly against this column,
        and the subset of rows is stored under `self.tables[long_key]`.
        """
        path = RESOURCES_DIR / "raw_NIHCD_feta_growth_calculator_percentile_range.tsv"
        if not path.exists():
            return

        df = _normalize_columns(pd.read_csv(path, sep="\t"))
        measure_col = next(
            (c for c in df.columns if c.strip().lower() == "measure"), None
        )
        if not measure_col:
            return

        # normalize the measure column for robust matching
        df[measure_col] = df[measure_col].str.strip().str.lower()

        for long_key, label in SUPPORTED_MEASURES.items():
            # build robust label set
            alias = SHORT_ALIASES.get(long_key, "")
            possible_labels = {
                label.lower(),
                alias.lower(),
                alias.upper(),
                label.lower().replace(" ", ""),
            }
            # add common synonyms
            if "circumference" in label.lower():
                possible_labels.add(label.lower().replace("circumference", "circ"))
            if long_key == "head_circumference":
                possible_labels.update({"hc", "headcirc", "headcircum"})

            # flexible substring matching
            subset = df[
                df[measure_col].apply(
                    lambda x: any(
                        lbl in x.replace(" ", "") for lbl in possible_labels if lbl
                    )
                )
            ]
            if not subset.empty:
                self.tables[long_key] = {"ct": _normalize_columns(subset)}

    # -----------------------
    # Public API
    # -----------------------

    def lookup_percentile(
        self, measurement_type: str, gestational_age_weeks: int, value_mm: float
    ) -> float:
        """
        Lookup the percentile of a measurement value at a given GA.

        Uses interpolation between bounding centile values if the
        measurement falls between two reference percentiles.
        """
        if measurement_type not in SUPPORTED_MEASURES:
            raise ValueError(f"Unsupported measurement type: {measurement_type}")

        if measurement_type not in self.tables:
            raise ValueError(
                f"No table for measurement '{measurement_type}' in source {self.source}"
            )

        df = self.tables[measurement_type]["ct"]
        row = df[df["Gestational Age (weeks)"] == gestational_age_weeks]
        if row.empty:
            raise ValueError(f"No reference data for GA={gestational_age_weeks}")

        # Collect percentile columns
        centile_cols = [c for c in df.columns if "percentile" in c.lower()]
        if not centile_cols:
            raise ValueError(
                f"No percentile columns found for {measurement_type} in source {self.source}"
            )

        # Interpolate observed value against row of reference values
        row_values = row[centile_cols].iloc[0].astype(float)
        return _interpolate_value_to_label(row_values, value_mm)

    def lookup_zscore(
        self, measurement_type: str, gestational_age_weeks: int, value_mm: float
    ) -> Optional[float]:
        """
        Lookup z-score of a measurement value at a given GA (if z-score table available).

        Uses interpolation between bounding z-scores. Returns None if
        z-score tables are not available (e.g., NIHCD).
        """
        if measurement_type not in SUPPORTED_MEASURES:
            raise ValueError(f"Unsupported measurement type: {measurement_type}")

        if measurement_type not in self.tables:
            raise ValueError(
                f"No table for measurement '{measurement_type}' in source {self.source}"
            )
        if "zs" not in self.tables[measurement_type]:
            return None  # NIHCD has no z-scores

        df = self.tables[measurement_type]["zs"]
        row = df[df["Gestational Age (weeks)"] == gestational_age_weeks]
        if row.empty:
            raise ValueError(f"No z-score data for GA={gestational_age_weeks}")

        # Collect z-score columns
        zscore_cols = [c for c in df.columns if "SD" in c]
        row_values = row[zscore_cols].iloc[0].astype(float)
        return _interpolate_value_to_label(row_values, value_mm)
