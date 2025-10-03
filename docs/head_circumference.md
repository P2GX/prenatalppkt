# Head Circumference

## Data sources
Head circumference percentile calculations use validated growth standards from:
- **NICHD fetal growth standards** (U.S. multi-ethnic prospective cohort).
- **INTERGROWTH-21st** (international, multi-site, population-agnostic standards).

Users may select which source to use depending on the dataset they are analyzing (e.g., NICHD may be appropriate for U.S. cohorts, while INTERGROWTH is designed for global application).  
The library defaults to **INTERGROWTH-21st** but supports both.

## Mapping strategy
1. Load reference centiles or z-scores for the chosen data source.
2. Look up expected distribution for the given gestational age.
3. Calculate:
  - **Z-score:** `(observed_value - mean) / sd`
  - **Percentile:** convert z-score to percentile via cumulative normal distribution.
4. Apply thresholds to infer ontology terms:
  - `< 3rd percentile` -> Microcephaly (HP:0000252)
  - `> 97th percentile` -> Macrocephaly (HP:0000256)
  - Otherwise, no abnormal HPO term.

## Extensions
- Supports multiple biometric measures (BPD, AC, FL, OFD, EFW).
- Integration with **Observer** and **Viewpoint** data, which may reference either NICHD or INTERGROWTH tables.