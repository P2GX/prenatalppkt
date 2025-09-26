# Biparietal Diameter (BPD)

## Data sources
- **INTERGROWTH-21st**: Provides *international* fetal growth standards for biparietal diameter in millimeters.  
 - Centile tables (3rd-97th):contentReference[oaicite:0]{index=0}.  
 - Z-score tables (-3 SD to +3 SD).  
- **NICHD**: U.S.-based, multi-ethnic cohort; percentiles stratified by maternal race/ethnicity.  

## Mapping strategy
- Look up the expected BPD at given gestational age in weeks.  
- Convert observed value into z-score or percentile.  
- Apply cutoffs (e.g., <10th percentile = small for gestational age).  

## Planned extensions
- Compare performance between NIHCD and INTERGROWTH references.  
- Add crosswalk functions so users can explicitly choose the reference standard.