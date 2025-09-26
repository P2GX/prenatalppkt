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

## INTERGROWTH-21st Fetal Growth Standards
The INTERGROWTH-21st Project established international fetal growth standards based on a multi-country study of low-risk pregnancies across diverse populations. Unlike NICHD, INTERGROWTH provides **single, population-agnostic reference tables** that are intended for global use.

Key features:
- Covers gestational ages 14-40 weeks.
- Provides both **centile tables** (3rd, 5th, 10th, 50th, 90th, 95th, 97th) and **z-score tables** (-3SD to +3SD).
- Includes multiple biometric measures:
 - Biparietal diameter (BPD)
 - Head circumference (HC)
 - Abdominal circumference (AC)
 - Femur length (FL)
 - Occipito-frontal diameter (OFD)

### Comparison to NICHD
- **NICHD:** stratified by maternal race/ethnicity, U.S.-specific.
- **INTERGROWTH:** pooled international data, ethnicity-agnostic.
- **Clinical use:** NICHD may be preferred in U.S. practice, while INTERGROWTH is more widely recommended in global and research contexts.

Reference: [INTERGROWTH-21st Fetal Growth Standards](https://intergrowth21.org/)

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
Hadlock and colleagues (1980s, Baylor College of Medicine, (see [**Key References**](#key-references))) developed widely used regression models to predict gestational age and estimated fetal weight (EFW) from ultrasound parameters.

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

### Key References
- [Radiology. 1984 Feb;150(2):535-40: *Sonographic estimation of fetal weight. The value of femur length in addition to head and abdomen measurements*](https://pubmed.ncbi.nlm.nih.gov/6691115/){:target="_blank"}
- [Am J Obstet Gynecol. 1985 Feb;151(3):333-7: *Estimation of fetal weight with the use of head, body, and femur measurements -- a prospective study*](https://www.sciencedirect.com/science/article/pii/0002937885902984?via%3Dihub){:target="_blank"}