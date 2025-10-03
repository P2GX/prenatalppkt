"""
normalize_tsv_to_csv.py

Convert parsed TSV reference tables (NIHCD + Intergrowth-21) into CSV format.
This ensures standardized, package-friendly data resources.

Input:
- data/parsed/raw_NIHCD_feta_growth_calculator_percentile_range.tsv
- data/parsed/intergrowth_text/*.tsv

Output:
- data/parsed/raw_NIHCD_feta_growth_calculator_percentile_range.csv
- data/parsed/intergrowth_text/*.csv

Usage:
$ python scripts/normalize_tsv_to_csv.py
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Directories
BASE_DIR = Path(__file__).resolve().parents[2]
PARSED_DIR = BASE_DIR / "data" / "parsed"


def convert_tsv_to_csv(tsv_path: Path) -> Path:
    """
    Convert a single TSV file to CSV with the same name.

    Parameters
    ----------
    tsv_path : Path
        Path to the input .tsv file.

    Returns
    -------
    Path
        Path to the generated .csv file.
    """
    df = pd.read_csv(tsv_path, sep="\t")
    csv_path = tsv_path.with_suffix(".csv")
    df.to_csv(csv_path, index=False)
    logger.info(f"Converted {tsv_path.name} -> {csv_path.name}")
    return csv_path


def main() -> None:
    """Main entry point: convert all known TSV files into CSVs."""
    targets = []

    # NIHCD single file
    nihcd_file = PARSED_DIR / "raw_NIHCD_feta_growth_calculator_percentile_range.tsv"
    if nihcd_file.exists():
        targets.append(nihcd_file)

    # Intergrowth parsed TSVs
    intergrowth_dir = PARSED_DIR / "intergrowth_text"
    if intergrowth_dir.exists():
        targets.extend(intergrowth_dir.glob("*.tsv"))

    if not targets:
        logger.warning("No TSV files found to convert.")
        return

    failed_conversions = []
    try:
        for tsv in targets:
            convert_tsv_to_csv(tsv)
    except Exception as exc:
        logger.error(f"Conversion process failed: {exc}")
        raise

    if failed_conversions:
        logger.error(f"Failed to convert {len(failed_conversions)} files:")
        for tsv, exc in failed_conversions:
            logger.error(f"- {tsv}: {exc}")


if __name__ == "__main__":
    main()
