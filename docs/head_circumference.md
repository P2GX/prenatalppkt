# Head Circumference

## Data source
Head circumference percentile calculations will use **NICHD fetal growth standards**.  
The current implementation uses **mock reference data** for 20 weeks only.

## Mapping strategy
1. Look up mean and standard deviation for the measurement at given gestational age.  
2. Calculate a z-score and convert it to a percentile using the normal distribution.  
3. Apply thresholds to infer ontology terms:
  - `< 3rd percentile` -> Microcephaly (HP:0000252)
  - `> 97th percentile` -> Macrocephaly (HP:0000256)
  - Otherwise, no term assigned.

## Planned extensions
- Replace mock reference with full NICHD tables across gestational ages.  
- Add population-specific standards if available.  
- Extend to other biometric measures (BPD, AC, FL, EFW).