# Fetal Growth Methods: NICHD Tables, Z-Scores, and Hadlock Regression

## NICHD Fetal Growth Tables
The Eunice Kennedy Shriver National Institute of Child Health and Human Development (NICHD) published growth standards for fetal biometry based on a large, multi-ethnic, prospective U.S. cohort. These tables provide percentile curves (3rd, 5th, 10th, 50th, 90th, 95th, 97th) for measurements such as:
- Biparietal diameter (BPD)
- Head circumference (HC)
- Abdominal circumference (AC)
- Femur length (FL)

The NICHD tables are stratified by maternal race/ethnicity (e.g., Non-Hispanic White, Non-Hispanic Black, Hispanic, Asian/Pacific Islander) and by gestational age in weeks. For example, at 20 weeks, the 50th percentile head circumference differs across populations. These tables serve as reference standards to determine whether a fetus is small-for-gestational-age (below the 10th percentile) or large-for-gestational-age (above the 90th percentile).

Reference: [NICHD Fetal Growth Calculator Percentile Range](https://www.nichd.nih.gov/sites/default/files/inline-files/FGCalculatorPercentileRange.pdf)

---

## Z-Scores
A z-score is a standardized measure that expresses how many standard deviations an observed value lies above or below the mean for a given gestational age and population. The formula is:

```
z = (observed_value - mean_for_age) / standard_deviation_for_age
```

- z = 0 means the value is exactly average for gestational age.
- z < -2 typically indicates growth restriction (e.g., microcephaly if applied to head circumference).
- z > +2 may indicate overgrowth (e.g., macrocephaly for head circumference).

Using z-scores rather than raw percentiles allows continuous assessment of growth across populations and enables combining measurements into regression-based models.

---

## Hadlock Regression Formulas
Hadlock and colleagues (1980s, Baylor College of Medicine) developed widely used regression models to predict gestational age and estimated fetal weight (EFW) from ultrasound parameters.

### Gestational Age Estimation
- **Parameters used:** BPD, HC, AC, FL (alone or in combination).
- **Finding:** Head circumference and femur length were the strongest individual predictors of age.
- **Regression model:** Multivariate polynomials including linear, quadratic, cubic, and interaction terms (e.g., HC, HC2, HC3, HC x FL).
- **Accuracy:** Combining parameters reduced variability compared to using BPD alone.

### Estimated Fetal Weight (EFW)
- **Parameters used:** HC, AC, FL (sometimes BPD).
- **Finding:** The best models combined at least three parameters (HC or BPD + AC + FL).
- **Accuracy:** Mean error about 0-2% with standard deviation of +-7-8% of actual birth weight.{index=2}
- **Clinical use:** Still widely employed in ultrasound machines for fetal weight estimation.

---

## Summary
- **NICHD tables** provide percentile-based norms stratified by race/ethnicity and gestational age.
- **Z-scores** standardize measurements relative to the mean, allowing precise classification of abnormal growth.
- **Hadlock regression formulas** predict gestational age and estimated fetal weight by combining multiple biometric parameters, reducing error compared to single measurements.