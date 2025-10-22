# Reference Data: Provenance and Usage

This library integrates two major sources of fetal growth standards:

## NICHD (U.S. Cohort-Based)
- Source: *Fetal Growth Calculator Percentile Range* (Eunice Kennedy Shriver NICHD).
- Stratified by maternal race/ethnicity: White, Black, Hispanic, Asian/Pacific Islander, and combined.
- Provides percentiles at each week of gestation (12-40 weeks).
- Reference: [NICHD FG Calculator PDF](https://www.nichd.nih.gov/sites/default/files/inline-files/FGCalculatorPercentileRange.pdf)

## INTERGROWTH-21st (International Cohort)
- Source: INTERGROWTH-21st Consortium, 2014-2020.
- Population-agnostic global reference.
- Provides both **centiles** and **z-scores** across 14-40 weeks.
- Measures: HC, BPD, AC, FL, OFD.

## Parsing Pipeline
1. Raw PDFs stored under `data/raw/`.
2. Converted to plain text (`.txt`) or parsed with **Docling**.
3. Normalized TSVs stored under `data/parsed/`.
4. Final CSV/TSV files packaged under `resources/percentiles/`.

## Library Integration
- `FetalGrowthPercentiles` loads NICHD or INTERGROWTH data.
- Users can specify `source="nichd"` or `source="intergrowth"`.
- Default: **INTERGROWTH-21st**.

## Observer & Viewpoint Context
- **Observer** datasets may be U.S.-centric and align with NICHD tables.
- **Viewpoint** datasets may be global and better matched to INTERGROWTH.
- This library supports both, with explicit source control.