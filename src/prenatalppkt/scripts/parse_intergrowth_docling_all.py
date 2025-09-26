"""
parse_intergrowth_docling_all.py

Batch-parse all Intergrowth-21 fetal growth tables (centiles and z-scores)
into TSVs. This script is designed to work across all the Intergrowth PDFs
with minimal user intervention.

We use **Docling** instead of lightweight PDF parsers because:
- The Intergrowth PDFs have **complex multi-row headers** (e.g. "Gestational age (exact weeks)" vs "Centiles.50 th").
- They contain **grid-structured medical tables**, which docling's
table-structure models (like TableFormer) handle better than plain OCR.
- Docling provides a single unified interface that outputs a structured
**TableItem -> pandas.DataFrame**, which we can normalize downstream.

This script differs from `parse_nichd_raw.py`:
- NIHCD parsing was simpler, since it dealt with a **text-based, single PDF** table.
- Intergrowth requires **looping across multiple PDFs and measures**, and handling
**both centile (_ct_) and z-score (_zs_) tables**.
- We also need fallback strategies because some tables won't parse
correctly on the first try (thus the multi-strategy extractor).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Docling handles PDF parsing + table structure reconstruction
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption


# -----------------------
# Defaults and renaming maps
# -----------------------

# Default folder for raw Intergrowth PDFs
DEFAULT_RAW_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "intergrowth21"
)
# Where normalized TSVs will be written
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "parsed"

# Mapping from filename keys to full measurement names
# (ensures TSVs are self-descriptive instead of cryptic codes)
MEASURE_MAP: Dict[str, str] = {
    "ac": "Abdominal Circumference",
    "bpd": "Biparietal Diameter",
    "fl": "Femur Length",
    "hc": "Head Circumference",
    "ofd": "Occipito-Frontal Diameter",
}

# Standardization for column names in centile (_ct_) tables
CT_COLUMN_RENAMES = {
    "GA": "Gestational Age (weeks)",
    "GA (weeks)": "Gestational Age (weeks)",
    "Gestational age (weeks)": "Gestational Age (weeks)",
    "3rd": "3rd Percentile",
    "5th": "5th Percentile",
    "10th": "10th Percentile",
    "50th": "50th Percentile",
    "90th": "90th Percentile",
    "95th": "95th Percentile",
    "97th": "97th Percentile",
}

# Desired order of centile columns (keeps outputs consistent across PDFs)
CT_COLUMNS_ORDER = [
    "Gestational Age (weeks)",
    "Measure",
    "3rd Percentile",
    "5th Percentile",
    "10th Percentile",
    "50th Percentile",
    "90th Percentile",
    "95th Percentile",
    "97th Percentile",
]


# -----------------------
# Helper functions
# -----------------------


def build_converter(
    do_table_structure: bool, do_cell_matching: Optional[bool]
) -> DocumentConverter:
    """
    Build a Docling DocumentConverter with flexible options.

    Why: Intergrowth PDFs vary in table layout quality. Some parse best with
    table-structure reconstruction, some without. This helper lets us build
    a converter with different strategies (structure, cell matching, etc).
    """
    pipeline = PdfPipelineOptions(do_table_structure=do_table_structure)
    if do_table_structure and do_cell_matching is not None:
        # TableFormer = ML-based model for reconstructing structured tables
        pipeline.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline.table_structure_options.do_cell_matching = do_cell_matching
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline)}
    )


def table_to_dataframe(tbl) -> pd.DataFrame:
    """
    Convert a Docling TableItem to a pandas DataFrame.

    Docling has two different APIs depending on version:
    - new: export_to_dataframe()
    - old: to_pandas()

    This keeps the script forward/backward compatible.
    """
    if hasattr(tbl, "export_to_dataframe"):
        return tbl.export_to_dataframe()
    elif hasattr(tbl, "to_pandas"):
        return tbl.to_pandas()
    else:
        raise AttributeError("Docling table object has no DataFrame export method.")


def try_extract_tables(pdf_path: Path, debug: bool = False) -> List[pd.DataFrame]:
    """
    Try multiple extraction strategies for a given PDF.

    Why: Some PDFs parse perfectly with table-structure ON, others require
    a looser mode. We iterate over three strategies:
    1. structure+match (most accurate, slowest)
    2. structure-no-match (fallback if cell matching is off)
    3. no-structure (raw text blocks -> tables)

    Returns a list of DataFrames (most PDFs only yield 1 table).
    """
    strategies: List[Tuple[bool, Optional[bool], str]] = [
        (True, True, "structure+match"),
        (True, False, "structure-no-match"),
        (False, None, "no-structure"),
    ]

    for do_struct, do_match, tag in strategies:
        converter = build_converter(do_struct, do_match)
        result = converter.convert(str(pdf_path))
        doc = result.document
        tables = list(doc.tables)

        if debug:
            logging.info(f"[{pdf_path.name}] strategy={tag} tables_found={len(tables)}")

        if not tables:
            continue

        frames: List[pd.DataFrame] = []
        for i, tbl in enumerate(tables):
            df: Optional[pd.DataFrame] = None
            try:
                df = table_to_dataframe(tbl)
            except Exception as exc:
                logging.warning(f"[{pdf_path.name}] {tag} table#{i} failed: {exc}")
            if df is not None and not df.empty:
                frames.append(df)
                if debug:
                    logging.info(
                        f"[{pdf_path.name}] {tag} table#{i} columns: {list(df.columns)}"
                    )

        if frames:
            return frames

    return []


def normalize_centile_table(
    df: pd.DataFrame, measure_label: str, debug: bool = False
) -> pd.DataFrame:
    """
    Normalize centile (_ct_) tables to a consistent schema.

    Steps:
    - Strip messy whitespace / multi-row headers
    - Standardize column names (e.g., "Centiles.50 th" -> "50th Percentile")
    - Add a "Measure" column (so one file encodes what biometric it refers to)
    - Reorder columns to match CT_COLUMNS_ORDER for downstream consistency
    """
    df.columns = [str(c).strip() for c in df.columns]

    # Some tables encode headers in the *first row* instead of column names
    if any(
        isinstance(v, str) and v.lower().startswith("ga") for v in df.iloc[0].to_numpy()
    ):
        df = df.rename(columns=df.iloc[0]).drop(df.index[0])
        df.columns = [str(c).strip() for c in df.columns]

    # Apply standard renaming map
    df = df.rename(columns={c: CT_COLUMN_RENAMES.get(c, c) for c in df.columns})

    # Insert "Measure" column if not already present
    if "Measure" not in df.columns:
        df.insert(1, "Measure", measure_label)

    # Reorder columns if possible, log missing columns otherwise
    if all(col in df.columns for col in CT_COLUMNS_ORDER):
        df = df[CT_COLUMNS_ORDER]
    else:
        cols = list(df.columns)
        for lead in ["Gestational Age (weeks)", "Measure"]:
            if lead in cols:
                cols.insert(0, cols.pop(cols.index(lead)))
        df = df[cols]
        if debug:
            missing = [c for c in CT_COLUMNS_ORDER if c not in df.columns]
            logging.info(f"Centile table missing columns: {missing}")

    return df


def write_tsv(df: pd.DataFrame, out_path: Path, force: bool) -> None:
    """
    Write DataFrame to TSV.

    We skip if the file exists unless --force is passed, to avoid
    unnecessary overwrites during repeated runs.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not force:
        logging.info(f"Exists (skip): {out_path}")
        return
    df.to_csv(out_path, sep="\t", index=False)
    logging.info(f"Wrote: {out_path}")


# -----------------------
# Main workflow
# -----------------------


def main() -> None:
    """Command-line entry point for parsing Intergrowth-21 PDFs. Scans the raw Intergrowth folder for centile (_ct_) and z-score (_zs_) tables, extracts them using Docling, normalizes the data, and writes structured TSVs under `data/parsed/`."""
    parser = argparse.ArgumentParser(
        description="Parse Intergrowth-21 PDFs (ct and zs) using Docling."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help="Path to intergrowth21 raw folder.",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Verbose table diagnostics."
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing TSV outputs."
    )
    parser.add_argument(
        "--only",
        choices=list(MEASURE_MAP.keys()),
        nargs="*",
        help="Restrict to specific measures (keys: ac bpd fl hc ofd).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    raw_dir = args.raw_dir.resolve()
    logging.info(f"RAW_DIR resolved to: {raw_dir}")

    # Find PDFs by pattern (ct = centile, zs = z-score)
    ct_pdfs = sorted(raw_dir.rglob("*ct*table.pdf"))
    zs_pdfs = sorted(raw_dir.rglob("*zs*table.pdf"))

    if not ct_pdfs and not zs_pdfs:
        logging.error(f"No PDFs found under {raw_dir}. Check filename patterns!")
        sys.exit(1)

    logging.info(f"Found ct PDFs: {len(ct_pdfs)}  |  zs PDFs: {len(zs_pdfs)}")

    # Process centile (_ct_) tables
    for pdf_path in ct_pdfs:
        # Match filename key (e.g., "_ac_" -> abdominal circumference)
        matched_key = next(
            (
                k
                for k in MEASURE_MAP
                if f"_{k}_" in pdf_path.stem or f"-{k}_" in pdf_path.stem
            ),
            None,
        )
        if not matched_key or (args.only and matched_key not in args.only):
            continue
        measure = MEASURE_MAP[matched_key]
        out_path = OUT_DIR / f"intergrowth21_{matched_key}_ct.tsv"

        logging.info(f"Parsing CT: {pdf_path.name}")
        frames = try_extract_tables(pdf_path, debug=args.debug)
        if not frames:
            logging.warning(f"No tables extracted from {pdf_path.name}")
            continue

        # Normalize before saving
        df_norm = normalize_centile_table(frames[0], measure, debug=args.debug)
        write_tsv(df_norm, out_path, force=args.force)

    # Process z-score (_zs_) tables
    for pdf_path in zs_pdfs:
        matched_key = next(
            (
                k
                for k in MEASURE_MAP
                if f"_{k}_" in pdf_path.stem or f"-{k}_" in pdf_path.stem
            ),
            None,
        )
        if not matched_key or (args.only and matched_key not in args.only):
            continue
        measure = MEASURE_MAP[matched_key]
        out_path = OUT_DIR / f"intergrowth21_{matched_key}_zs.tsv"

        logging.info(f"Parsing ZS: {pdf_path.name}")
        frames = try_extract_tables(pdf_path, debug=args.debug)
        if not frames:
            logging.warning(f"No tables extracted from {pdf_path.name}")
            continue

        # Z-score tables are simpler (already numeric bins), so no heavy normalization
        df = frames[0]
        df.columns = [str(c).strip() for c in df.columns]
        if "Measure" not in df.columns:
            df.insert(1, "Measure", measure)

        write_tsv(df, out_path, force=args.force)


if __name__ == "__main__":
    main()
