```markdown
# Documentation: ViewPoint Dropdown Lists Integration and Conversion
## Overview
This document describes the structure and purpose of the `ViewPoint` dropdown list definition files (.vpl) found in exported configurations from GE ViewPoint 6 ultrasound reporting systems, and how they can be parsed and converted for integration with the `prenatalppkt` library.

The ViewPoint dropdown list files define structured reporting options used in sonography templates (e.g., Fetal Anatomy, Abdominal Cavity, Cardiac Activity). Each list contains items corresponding to possible findings or interpretations entered in clinical ultrasound reports.

The goal of this process is to convert the proprietary `.vpl` text format into open, structured formats (.csv or .json) that can later be mapped to ontology terms or used for harmonizing report data into machine-readable Phenopackets.

## File Origin and Structure
A ViewPoint export typically contains:
* `viewpoint.zip`, `observer.zip`, or similar archives.
* A folder such as `VPLists/` containing hundreds of `.vpl` files.

Each `.vpl` file defines a single dropdown list (for example, `AbdomenFetus_AbdominalCavityAppearance.vpl`) and is encoded as UTF-16 Little Endian text.

Example file header (simplified):
```text
"6.14.2" "AbdomenFetus_AbdominalCavityAppearance"
Item Name   Parent Name   Label Short@English_US
"appears_normal"  ""  "Appears normal"
"abnormal"        ""  "Abnormal"
"suboptimal"      ""  "Suboptimal"
```
Each row corresponds to one selectable item in the ViewPoint reporting interface.

## Relationship to prenatalppkt
In the `prenatalppkt` project, structured dropdown data from ViewPoint or Observer systems can be used to:
* Map categorical ultrasound findings (e.g., "appears normal", "abnormal") to ontology terms
* Normalize ViewPoint report fields to machine-readable formats compatible with Phenopacket export.
* Support harmonization across different reporting systems (U.S.-centric ViewPoint vs Observer datasets).

The `.vpl` parsing process does not perform growth analysis directly, but provides standardized metadata that complements the quantitative measurement layer described in the main project documentation (e.g., mapping exam findings to structured feature terms).

## Conversion Goals
* Convert each `.vpl` file to an individual UTF-8 CSV file.
* Optionally merge all `.vpl` files into a single combined CSV and JSON dataset.
* Store the converted outputs under `data/parsed/ViewPoint/drop_down_options/`.

## Directory Structure
Example integration within the `prenatalppkt` repository:
```text
data/raw/VPLists/
AbdomenFetus_AbdominalCavityAppearance.vpl
HeartFetus_CardiacActivity.vpl
...
parsed/
ViewPoint/
drop_down_options/
AbdomenFetus_AbdominalCavityAppearance.csv
HeartFetus_CardiacActivity.csv
All_ViewPoint_Lists.csv
All_ViewPoint_Lists.json
```

## Python Conversion Script (Individual Files)
Save the following as `convert_vpl_to_csv.py`:
```python
import csv
import os
import glob
# Directory where .vpl files are stored
VPL_DIR = "data/raw/VPLists"
OUTPUT_DIR = "data/parsed/ViewPoint/drop_down_options"
os.makedirs(OUTPUT_DIR, exist_ok=True)
for filepath in glob.glob(os.path.join(VPL_DIR, "*.vpl")):
   with open(filepath, "r", encoding="utf-16") as f:
       lines = [line.strip() for line in f if line.strip()]
   if len(lines) < 3:
       continue
   header_line = lines[2]
   headers = header_line.split("\t")
   data_lines = lines[3:]
   output_filename = os.path.splitext(os.path.basename(filepath))[0] + ".csv"
   output_path = os.path.join(OUTPUT_DIR, output_filename)
   with open(output_path, "w", newline='', encoding="utf-8") as out_csv:
       writer = csv.writer(out_csv)
       writer.writerow(headers)
       for line in data_lines:
           writer.writerow(line.split("\t"))
   print(f"Converted {filepath} -> {output_filename}")
```
Run the script:
```bash
python3 convert_vpl_to_csv.py
```
Each ViewPoint list becomes an individual UTF-8 CSV file.

## Combined Conversion Script (All-in-One CSV and JSON)
Save the following as `combine_vpl_lists.py`:
```python
import csv
import json
import glob
import os
VPL_DIR = "data/raw/VPLists"
OUTPUT_CSV = "data/parsed/ViewPoint/drop_down_options/All_ViewPoint_Lists.csv"
OUTPUT_JSON = "data/parsed/ViewPoint/drop_down_options/All_ViewPoint_Lists.json"
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
all_data = []
for filepath in glob.glob(os.path.join(VPL_DIR, "*.vpl")):
   filename = os.path.basename(filepath)
   list_name = os.path.splitext(filename)[0]
   try:
       with open(filepath, "r", encoding="utf-16") as f:
           lines = [line.strip() for line in f if line.strip()]
   except Exception as e:
       print(f"Skipping {filename}: {e}")
       continue
   if len(lines) < 4:
       continue
   headers = lines[2].split("\t")
   data_lines = lines[3:]
   for line in data_lines:
       values = line.split("\t")
       row = dict(zip(headers, values))
       row["__SourceFile"] = filename
       row["__ListName"] = list_name
       all_data.append(row)
print(f"Parsed {len(all_data)} total dropdown items.")
csv_headers = sorted({key for row in all_data for key in row.keys()})
with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as out_csv:
   writer = csv.DictWriter(out_csv, fieldnames=csv_headers)
   writer.writeheader()
   writer.writerows(all_data)
with open(OUTPUT_JSON, "w", encoding="utf-8") as out_json:
   json.dump(all_data, out_json, ensure_ascii=False, indent=2)
print("Wrote combined CSV and JSON outputs.")
```
Run the script:
```bash
python3 combine_vpl_lists.py
```

## Quick Terminal Preview
For quick inspection of a single file in a terminal (Linux or macOS):
```bash
iconv -f UTF-16LE -t UTF-8 AbdomenFetus_AbdominalCavityAppearance.vpl | column -ts $'\t' | less
```

## Batch Conversion (Shell One-Liner)
To convert all files to plain CSV text in bash:
```bash
mkdir -p data/parsed/ViewPoint/drop_down_options
for f in data/raw/VPLists/*.vpl; do
iconv -f UTF-16LE -t UTF-8 "$f" | sed '1,2d' > \
"data/parsed/ViewPoint/drop_down_options/$(basename "${f%.vpl}.csv")"
done
```

## Output Examples
Example of a converted CSV entry:
```text
__SourceFile,__ListName,Item Name,Label Short@English_US,Item Type,Parent Name
AbdomenFetus_AbdominalCavityAppearance.vpl,AbdomenFetus_AbdominalCavityAppearance,appears_normal,Appears normal,Item,
AbdomenFetus_AbdominalCavityAppearance.vpl,AbdomenFetus_AbdominalCavityAppearance,abnormal,Abnormal,Item,
```

Example JSON structure:
```json
[
{
"__SourceFile": "AbdomenFetus_AbdominalCavityAppearance.vpl",
"__ListName": "AbdomenFetus_AbdominalCavityAppearance",
"Item Name": "appears_normal",
"Label Short@English_US": "Appears normal",
"Item Type": "Item"
},
...
]
```

## Integration Use Case
After conversion, the resulting structured lists can be imported into the `prenatalppkt` workflow for ontology mapping or harmonization tasks:
* Map categorical dropdown values to Human Phenotype Ontology (HPO) or ICD-10 codes.
* Normalize ultrasound report metadata before quantitative analysis.
* Provide reference vocabulary alignment between ViewPoint, Observer, and Phenopacket representations.

## Summary
* ViewPoint `.vpl` files define ultrasound report dropdown options.
* The provided scripts convert them to portable CSV/JSON data.
* Output can be used by `prenatalppkt` for ontology-based harmonization.
* All text encoding is handled (UTF-16 to UTF-8), preserving multilingual content if present.
```