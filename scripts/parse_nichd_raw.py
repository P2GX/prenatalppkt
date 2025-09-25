"""
parse_nichd_raw.py

Parse the NIHCD fetal growth percentile tables from plain text into
a structured TSV file. Cleans out headers, page markers, and stray
percentile-only rows.
"""

import csv
from pathlib import Path
from typing import Optional, List

# Paths
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_FILE = DATA_DIR / "raw" / "raw_NIHCD_feta_growth_calculator_percentile_range_text.txt"
OUT_FILE = DATA_DIR / "parsed" / "raw_NIHCD_feta_growth_calculator_percentile_range.tsv"


def normalize_measure(parts: List[str]) -> str:
   """Normalize measurement tokens like Circ -> Circ."""
   if len(parts) == 2 and parts[1] == "Circ":
       return f"{parts[0]} Circ."
   return " ".join(parts)


def is_header_or_junk(line: str) -> bool:
   """Detect NIHCD headers, junk rows, or page markers."""
   line = line.strip()

   # Skip completely empty lines
   if not line:
       return True

   # Skip known junk text
   junk_markers = [
       "Fetal Growth Calculator",
       "Gestational",
       "Percentile",
       "Age (weeks)",
   ]
   if any(marker in line for marker in junk_markers):
       return True

   # Skip standalone percentile labels
   percentile_labels = {"3rd", "5th", "10th", "50th", "90th", "95th", "97th"}
   if line in percentile_labels:
       return True

   # Skip page markers like "- 1 -"
   if line.startswith("-") and line.endswith("-"):
       return True

   return False


def parse_line(line: str) -> Optional[List[str]]:
   """Parse one line into structured columns."""
   if is_header_or_junk(line):
       return None

   tokens = line.strip().split()
   if not tokens:
       return None

   try:
       ga = tokens[0]  # gestational age
       measurement_keywords = {"Abdominal", "Head", "Femur", "Biparietal"}

       race_tokens = []
       measure_tokens = []
       idx = 1

       # Collect race tokens until measurement keyword
       while idx < len(tokens):
           if tokens[idx] in measurement_keywords:
               break
           race_tokens.append(tokens[idx])
           idx += 1

       # Collect measure tokens until numbers
       while idx < len(tokens) and not tokens[idx].replace(".", "", 1).isdigit():
           measure_tokens.append(tokens[idx])
           idx += 1

       race = " ".join(race_tokens)
       measure = normalize_measure(measure_tokens)
       percentiles = tokens[idx:]

       return [ga, race, measure] + percentiles
   except Exception:
       return None


def main() -> None:
   """Main entry point: parse NIHCD raw text to TSV."""
   OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

   with RAW_FILE.open("r", encoding="utf-8") as fin, OUT_FILE.open("w", newline="", encoding="utf-8") as fout:
       writer = csv.writer(fout, delimiter="\t", quoting=csv.QUOTE_MINIMAL)

       # Header row
       writer.writerow([
           "Gestational Age (weeks)",
           "Race",
           "Measure",
           "3rd Percentile",
           "5th Percentile",
           "10th Percentile",
           "50th Percentile",
           "90th Percentile",
           "95th Percentile",
           "97th Percentile",
       ])

       for raw_line in fin:
           row = parse_line(raw_line)
           if row:
               writer.writerow(row)

   print(f"Parsed data written to {OUT_FILE}")


if __name__ == "__main__":
   main()