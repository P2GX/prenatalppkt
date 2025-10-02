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

import pandas as pd
from pathlib import Path
from typing import Dict, Optional


# -----------------------
# Paths and supported measures
# -----------------------

RESOURCES_DIR = Path(__file__).resolve().parents[2] / "data" / "parsed"

SUPPORTED_MEASURES = {
    "head_circumference": "Head Circumference",
    "biparietal_diameter": "Biparietal Diameter",
    "abdominal_circumference": "Abdominal Circumference",
    "femur_length": "Femur Length",
    "occipitofrontal_diameter": "Occipito-Frontal Diameter",
}


class FetalGrowthPercentiles:
    """
    Load fetal growth percentiles and z-scores for multiple biometrics.

    Attributes
    ----------
    source : str
        "intergrowth" (default) or "nichd".
    tables : Dict[str, pd.DataFrame]
        Dictionary mapping measure keys ("hc", "bpd", etc.) to parsed DataFrames.
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
        """Load all reference tables for the selected source into memory."""
        if self.source == "intergrowth":
            for key in SUPPORTED_MEASURES:
                ct_path = (
                    RESOURCES_DIR
                    / "intergrowth21_docling_parse"
                    / f"intergrowth21_{key}_ct.tsv"
                )
                zs_path = (
                    RESOURCES_DIR
                    / "intergrowth21_docling_parse"
                    / f"intergrowth21_{key}_zs.tsv"
                )
                if ct_path.exists() and zs_path.exists():
                    ct_df = pd.read_csv(ct_path, sep="\t")
                    zs_df = pd.read_csv(zs_path, sep="\t")
                    self.tables[key] = {"ct": ct_df, "zs": zs_df}
        elif self.source == "nichd":
            path = (
                RESOURCES_DIR / "raw_NIHCD_feta_growth_calculator_percentile_range.tsv"
            )
            if path.exists():
                df = pd.read_csv(path, sep="\t")
                # Split into measures for consistency
                for key, measure in SUPPORTED_MEASURES.items():
                    subset = df[df["Measure"].str.contains(measure)]
                    if not subset.empty:
                        self.tables[key] = {"ct": subset}

    # -----------------------
    # Public API
    # -----------------------

    def lookup_percentile(
        self, measure_key: str, gestational_age_weeks: int, value_mm: float
    ) -> float:
        """
        Lookup the percentile of a measurement value at a given GA.

        Parameters
        ----------
        measure_key : str
            One of {"hc", "bpd", "ac", "fl", "ofd"}.
        gestational_age_weeks : int
            Gestational age in completed weeks.
        value_mm : float
            Measured value in millimeters.

        Returns
        -------
        float
            Percentile (0-100).

        Raises
        ------
        ValueError
            If measure is not supported or GA is out of range.
        """
        if measure_key not in self.tables:
            raise ValueError(
                f"No table for measure '{measure_key}' in source {self.source}"
            )

        df = self.tables[measure_key]["ct"]
        if "Gestational Age (weeks)" not in df.columns:
            raise ValueError("Reference table missing GA column")

        row = df[df["Gestational Age (weeks)"] == gestational_age_weeks]
        if row.empty:
            raise ValueError(f"No reference data for GA={gestational_age_weeks}")

        # Find closest centile by absolute difference
        centile_cols = [c for c in df.columns if "Percentile" in c]
        row_values = row[centile_cols].iloc[0].astype(float)
        diffs = (row_values - value_mm).abs()
        closest_col = diffs.idxmin()

        # Column like "50th Percentile" -> 50
        percentile = float(
            closest_col.split()[0]
            .replace("th", "")
            .replace("rd", "")
            .replace("st", "")
            .replace("nd", "")
        )
        return percentile

    def lookup_zscore(
        self, measure_key: str, gestational_age_weeks: int, value_mm: float
    ) -> Optional[float]:
        """
        Lookup z-score of a measurement value at a given GA (if z-score table available).

        Returns None if z-score tables are not available (e.g., NIHCD).

        Raises
        ------
        ValueError
            If GA is out of range or measure unsupported.
        """
        if measure_key not in self.tables:
            raise ValueError(
                f"No table for measure '{measure_key}' in source {self.source}"
            )
        if "zs" not in self.tables[measure_key]:
            return None  # NIHCD has no z-scores

        df = self.tables[measure_key]["zs"]
        if "Gestational Age (weeks)" not in df.columns:
            raise ValueError("Reference z-score table missing GA column")

        row = df[df["Gestational Age (weeks)"] == gestational_age_weeks]
        if row.empty:
            raise ValueError(f"No z-score data for GA={gestational_age_weeks}")

        # Find closest z-score column by absolute difference
        zscore_cols = [c for c in df.columns if "SD" in c]
        row_values = row[zscore_cols].iloc[0].astype(float)
        diffs = (row_values - value_mm).abs()
        closest_col = diffs.idxmin()

        # Column like "-2 SD" -> -2
        zscore = float(closest_col.split()[0])
        return zscore
