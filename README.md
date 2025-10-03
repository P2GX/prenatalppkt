# prenatalppkt
==============

Library to transform raw sonography data into [Phenopackets](https://phenopacket-schema.readthedocs.io/) with validated fetal growth references (NIHCD and INTERGROWTH-21st).

-------------------------------------------------------------------------------
## Why
-------------------------------------------------------------------------------
- Standardize prenatal phenotype reporting for cases paired with WES/WGS.
- Enable federated repositories using consistent machine-readable formatting.
- Provide clinically valid percentile and z-score calculations from authoritative growth standards.

-------------------------------------------------------------------------------
## Inputs and Outputs (at a glance)
-------------------------------------------------------------------------------
### Inputs
- **Observer JSON** (e.g. `data/EVMS_SAMPLE.json`)
- **ViewPoint Excel workbook** (`.xlsx` / `.xls`) with fetal biometry rows
- Typical sections:
  - * exam: DOB, LMP, GA by dates, exam date, ICD-10, referring clinicians
  - * fetuses[*]: anatomy blocks, measurements, vessels, procedures

### Outputs
- **Phenopackets (v2)**: one JSON per fetus (default) or per pregnancy (configurable)
  * subject: pseudo-ID for fetus; optional family link/pedigree
  * phenotypicFeatures: HPO terms with gestational onset (via ontology mapping)
  * measurements: BPD / HC / AC / FL / OFD, EFW, ratios
  * diseases: ICD-10 indications; optional MONDO/OMIM mappings
  * metaData: versioning, ontology versions, pipeline provenance
- **QC reports** per input record with structured issues
- **Optional flat CSV** with per-fetus features for downstream analysis

-------------------------------------------------------------------------------
## Simple Architecture
--------------------------------------------------------

          +-----------------------+
          | Input JSON / XLSX     |
          +-----------------------+
                    |
                    v
          +-----------------------+
          | Parser Layer          |
          | - Extracts GA, HC,    |
          |   BPD, AC, FL, OFD    |
          +-----------------------+
                    |
                    v
          +-----------------------+
          | Reference Lookup      |
          | - FetalGrowthPercent  |
          |   loads NIHCD/IG21st  |
          | - Percentile/Z-score  |
          +-----------------------+
                    |
                    v
          +-----------------------+
          | BiometryMeasurement   |
          | - Maps values to HPO  |
          | - Flags abnormalities |
          +-----------------------+
                    |
                    v
          +-----------------------+
          | Phenopacket Builder   |
          | - JSON assembly       |
          | - Metadata/QC log     |
          +-----------------------+
                    |
           +--------+--------+
           |                 |
           v                 v
  +----------------+   +----------------+
  | QC Reports     |   | Phenopackets   |
  +----------------+   +----------------+

Optional: extract flat CSV for statistical analysis.

-------------------------------------------------------------------------------
## Core Components (src/prenatalppkt/)
-------------------------------------------------------------------------------
- `biometry.py`
   - Defines `BiometryMeasurement` and `BiometryType`. Wraps reference lookups and applies abnormality logic (<=3rd percentile or >=97th percentile) to assign HPO terms.

- `biometry_reference.py`
   - Provides `FetalGrowthPercentiles`, which loads validated growth tables.
   - Supports:
      - * INTERGROWTH-21st (centiles + z-scores for HC, BPD, AC, FL, OFD).
      - * NICHD (percentiles for HC, BPD, AC, FL, EFW).

- `constants.py`
   Defines ontology mappings (e.g. HPO_MICROCEPHALY = HP:0000252).

- `qc/` (planned)
   Will validate completeness, gestational ages, duplicate measures, and flag out-of-range data.

- `phenopacket_builder/` (planned)
   Will convert parsed + annotated measurements into full [GA4GH Phenopacket v2](https://phenopacket-schema.readthedocs.io/en/latest/) JSONs.

Together:
**Inputs -> parsed measurements -> percentile/z-score lookup -> abnormality detection (HPO terms) -> structured Phenopacket**

-------------------------------------------------------------------------------
## Mapping to Phenopackets
-------------------------------------------------------------------------------
Our mapping strategy combines biometric reference lookups with ontology terms:

1. **Parse biometry** from JSON/XLSX. Extract GA (weeks) and raw measurement values (mm).
2. **Reference lookup** with `FetalGrowthPercentiles`:
* Find percentile for the measurement at given GA.
* Compute z-score (if INTERGROWTH source).
3. **Abnormality thresholds**:
* If value <=3rd percentile -> assign *small/short* phenotype HPO (e.g. microcephaly, short femur).
* If value >=97th percentile -> assign *large/long* phenotype HPO (e.g. macrocephaly, long femur).
* Otherwise, no HPO abnormality.
4. **Assemble Phenopacket**:
* `subject`: pseudo-ID for fetus.
* `phenotypicFeatures`: HPO terms with `onset=GA`.
* `measurements`: raw values + units, linked to ontology type.
* `diseases`: ICD-10 indications from input.
* `metaData`: pipeline + version information.

This ensures **machine-readable, clinically valid prenatal phenotyping** from raw sonography.

-------------------------------------------------------------------------------
## Example Usage
-------------------------------------------------------------------------------
```python
from prenatalppkt.biometry import BiometryMeasurement, BiometryType
from prenatalppkt.biometry_reference import FetalGrowthPercentiles

fg = FetalGrowthPercentiles(source="intergrowth")

measure = BiometryMeasurement(
   measurement_type=BiometryType.HEAD_CIRCUMFERENCE,
   gestational_age_weeks=22,
   value_mm=196.3,
)

percentile, hpo = measure.percentile_and_hpo(reference=fg)
print(percentile, hpo)
# Example: 50.0, None

```

## Testing

### Run linting and tests:
ruff format . && ruff check . --fix && pytest -vv

### Tests cover:
# Normal vs abnormal growth (HC, BPD, AC, FL, OFD)
# Z-score lookups (INTERGROWTH only)
# Missing reference data
# Unsupported measurement types
# Interpolation for non-tabled gestational ages

# Documentation
# docs/reference_data.md: data provenance, parsing workflow, and usage notes.
# Future docs: input parsers, QC pipeline, end-to-end phenopacket export.

# CLI quick start (planned):
# prenatalppkt parse --input mydata.xlsx --output outdir/