# prenatalppkt Documentation

This site documents the prenatalppkt library.

## Overview
- Transforms raw ultrasound biometry into standardized **Phenopackets (v2)**.
- Supports both **NICHD** and **INTERGROWTH-21st** fetal growth standards.
- Provides percentile and z-score calculations for multiple biometric measures.

## Key Topics
- [Head Circumference](head_circumference.md)
- [Biparietal Diameter](biparietal_diameter.md)
- [Abdominal Circumference](abdominal_circumference.md)
- [Femur Length](femur_length.md)
- [Occipito-Frontal Diameter](occipitofrontal_diameter.md)
- [Reference Data](reference_data.md)
- [Fetal Growth Methods](fetal_growth_methods.md)
- [Internal Dev Notes](internal.md)

## Quickstart
```python
from prenatalppkt.biometry_reference import FetalGrowthPercentiles
ref = FetalGrowthPercentiles(source="intergrowth")
pct = ref.lookup_percentile("head_circumference", 20, 175)