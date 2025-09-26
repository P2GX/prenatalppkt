"""
parse_intergrowth_txt_all.py

Robust rule-based parser for Intergrowth-21 fetal growth tables extracted into plain text.
Produces clean TSVs for each measurement and table type (centiles and z-scores).

Input:
data/raw/intergrowth21/*/*_ct_*_table.txt
data/raw/intergrowth21/*/*_zs_*_table.txt

Output:
data/parsed/intergrowth_text/intergrowth21_<measure>_ct.tsv
data/parsed/intergrowth_text/intergrowth21_<measure>_zs.tsv

Dependencies:
pip install pandas
"""

from pathlib import Path
from typing import List, Dict
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# -----------------------
# Paths
# -----------------------

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "intergrowth21"
OUT_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "parsed" / "intergrowth_text"
)

# -----------------------
# Metadata
# -----------------------

MEASURE_MAP = {
    "ac": "Abdominal Circumference",
    "bpd": "Biparietal Diameter",
    "fl": "Femur Length",
    "hc": "Head Circumference",
    "ofd": "Occipito-Frontal Diameter",
}

CT_HEADERS = [
    "Gestational Age (weeks)",
    "3rd Percentile",
    "5th Percentile",
    "10th Percentile",
    "50th Percentile",
    "90th Percentile",
    "95th Percentile",
    "97th Percentile",
]

ZS_HEADERS = [
    "Gestational Age (weeks)",
    "-3 SD",
    "-2 SD",
    "-1 SD",
    "0 SD",
    "1 SD",
    "2 SD",
    "3 SD",
]

EXPECTED_GA_RANGE = list(range(14, 41))  # 14-40 inclusive


# -----------------------
# Helpers
# -----------------------


def clean_line(line: str) -> str:
    """Normalize whitespace and strip line."""
    return " ".join(line.strip().split())


def is_data_line(line: str) -> bool:
    """Detect numeric data lines by checking if first token is a number."""
    parts = line.split()
    if not parts:
        return False
    return parts[0].replace(".", "", 1).isdigit()


def parse_table(
    lines: List[str],
    headers: List[str],
    measure: str,
    source: str,
    summary: Dict[str, Dict[str, int]],
) -> pd.DataFrame:
    """
    Parse a block of lines into a DataFrame with headers + Measure column.
    Skips malformed rows and validates numeric columns.
    """
    records = []
    malformed = 0
    for line in lines:
        if not is_data_line(line):
            continue
        row = line.split()
        if len(row) != len(headers):
            malformed += 1
            continue
        records.append(row)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records, columns=headers)
    df.insert(1, "Measure", measure)

    # Coerce numeric columns
    for col in df.columns:
        if col not in ["Measure", "SourceFile", "ParseTimestamp"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing GA or malformed numbers
    df = df.dropna()

    # GA sanity check
    bad_ga = [
        ga
        for ga in df["Gestational Age (weeks)"].astype(int).tolist()
        if ga not in EXPECTED_GA_RANGE
    ]
    if bad_ga:
        logger.warning("Unexpected GA values in %s: %s", source, bad_ga)

    # Provenance
    df["SourceFile"] = source
    df["ParseTimestamp"] = datetime.now().isoformat(timespec="seconds")

    # Update summary
    summary[source] = {
        "parsed": len(df),
        "malformed": malformed,
        "skipped_na": len(records) - len(df),
    }

    return df


def parse_txt_file(
    file_path: Path, measure: str, table_type: str, summary: Dict[str, Dict[str, int]]
) -> pd.DataFrame:
    """
    Parse a single Intergrowth text file (centiles or z-scores).
    """
    lines = [clean_line(line) for line in file_path.read_text().splitlines()]
    headers = CT_HEADERS if table_type == "ct" else ZS_HEADERS
    return parse_table(lines, headers, measure, file_path.name, summary)


def write_tsv(df: pd.DataFrame, out_path: Path) -> None:
    """Write DataFrame to TSV file, creating directories as needed."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, sep="\t", index=False)
    logger.info("Wrote %s", out_path)


# -----------------------
# Main
# -----------------------


def main() -> None:
    """Main driver: parse all per-measure .txt files into TSVs."""
    summary: Dict[str, Dict[str, int]] = {}

    for key, measure in MEASURE_MAP.items():
        ct_files = list(RAW_DIR.rglob(f"*ct_{key}_table.txt"))
        zs_files = list(RAW_DIR.rglob(f"*zs_{key}_table.txt"))

        for file_path in ct_files:
            df = parse_txt_file(file_path, measure, "ct", summary)
            if not df.empty:
                out_path = OUT_DIR / f"intergrowth21_{key}_ct.tsv"
                write_tsv(df, out_path)

        for file_path in zs_files:
            df = parse_txt_file(file_path, measure, "zs", summary)
            if not df.empty:
                out_path = OUT_DIR / f"intergrowth21_{key}_zs.tsv"
                write_tsv(df, out_path)

    # -------- Summary --------
    logger.info("\n=== Parse Summary ===")
    for fname, stats in summary.items():
        logger.info(
            f"{fname:40s} | rows={stats['parsed']:3d} "
            f"(malformed={stats['malformed']}, dropped_na={stats['skipped_na']})"
        )


if __name__ == "__main__":
    main()
