# prenatalppkt
============

Library to transform raw sonagraphy data into phenopackets

-------------------------------------------------------------------------------
## Why
-------------------------------------------------------------------------------
- Standardize prenatal phenotype reporting for cases paired with WES/WGS.
- Enable federated repositories using consistent machine-readable formatting
-------------------------------------------------------------------------------
## Inputs and Outputs (at a glance)
-------------------------------------------------------------------------------
### Inputs
- **Observer JSON** (such as `data/EVMS_SAMPLE.json`).
- **ViewPoint Excel workbook** (`.xlsx`/`.xls`) with fetal biometry rows.
- Typical sections:
   * exam:           DOB, LMP, GA by dates, exam date, ICD-10, referring clinicians
   * fetuses[*]:     anatomy blocks, measurements, vessels, procedures

### Outputs
- **Phenopackets (v2)** - one JSON per fetus (default) or per pregnancy (configurable):
   * subject:              pseudo-ID for fetus; optional family link/pedigree later
   * phenotypicFeatures:   HPO terms with gestational onset (via ontology mapping)
   * measurements:         BPD/HC/AC/FL, EFW, ratios (with UO units, ultrasound method)
   * diseases:             ICD-10 indications; optional MONDO/OMIM mappings
   * metaData:             versioning, ontology versions, pipeline provenance
- Ω
- **QC reports** per input record with structured issues

### Output layout
- Ω
   - Ω
      - Ω
   - Ω
      - Ω

-------------------------------------------------------------------------------
## Simple Architecture
-------------------------------------------------------------------------------

               +---------------------+
               |   Input JSON/XLSX   |
               +----------+----------+
                          |
                          v
               +----------+----------+
               |          Ω          |
               |                     |
               +----------+----------+
                          |
                          v
               +----------+----------+
               |          Ω          |
               +----------+----------+
                          |
                          v
               +----------+----------+
               |          Ω          |
               +----------+----------+
                          |
                          v
               +----------+----------+
               | Phenopacket builder |
               |                     |
               +----------+----------+
                          |
         +----------------+-----------------+
         |                                  |
         v                                  v
   +-----+-----+                     +------+------+
   | QC reports|                     | Phenopackets|
   +-----------+                     +-------------+

Optional: extract flat CSV features for analysis.

-------------------------------------------------------------------------------
## Core components (src/fetalpackets/)
-------------------------------------------------------------------------------
- Ω               : Ω
-------------------------------------------------------------------------------
## Intermediate Representation (IR)
-------------------------------------------------------------------------------
- Ω

-------------------------------------------------------------------------------
## QC
-------------------------------------------------------------------------------
- Ω

-------------------------------------------------------------------------------
## Mapping to Phenopackets
-------------------------------------------------------------------------------
- Ω

-------------------------------------------------------------------------------
## Feature extraction (optional)
-------------------------------------------------------------------------------
Goal
- Flat, analysis-ready CSV with per-fetus features and simple classification
 (e.g., BPD class using a reference table).

-------------------------------------------------------------------------------
## CLI quick start
-------------------------------------------------------------------------------
- Ω