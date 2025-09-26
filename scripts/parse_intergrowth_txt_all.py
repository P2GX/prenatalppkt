"""
parse_intergrowth_txt_all.py

Rule-based parser for Intergrowth-21 fetal growth tables extracted into plain text. Produces clean TSVs for each measurement and table type (centiles and z-scores).

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
from typing import List
import pandas as pd

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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


def parse_table(lines: List[str], headers: List[str], measure: str) -> pd.DataFrame:
    """Parse a block of lines into a DataFrame with headers + Measure column."""
    records = []
    for line in lines:
        if not is_data_line(line):
            continue
        records.append(line.split())

    df = pd.DataFrame(records)
    if not df.empty:
        df.columns = headers
        df.insert(1, "Measure", measure)
    return df


def parse_txt_file(file_path: Path, measure: str, table_type: str) -> pd.DataFrame:
    """
    Parse a single Intergrowth text file (centiles or z-scores).
    """
    lines = [clean_line(line) for line in file_path.read_text().splitlines()]
    headers = CT_HEADERS if table_type == "ct" else ZS_HEADERS
    return parse_table(lines, headers, measure)


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
    for pdf_key, measure in MEASURE_MAP.items():
        # centile and z-score text files
        ct_files = list(RAW_DIR.rglob(f"*ct_{pdf_key}_table.txt"))
        zs_files = list(RAW_DIR.rglob(f"*zs_{pdf_key}_table.txt"))

        for file_path in ct_files:
            df = parse_txt_file(file_path, measure, "ct")
            if not df.empty:
                out_path = OUT_DIR / f"intergrowth21_{pdf_key}_ct.tsv"
                write_tsv(df, out_path)

        for file_path in zs_files:
            df = parse_txt_file(file_path, measure, "zs")
            if not df.empty:
                out_path = OUT_DIR / f"intergrowth21_{pdf_key}_zs.tsv"
                write_tsv(df, out_path)


if __name__ == "__main__":
    main()
