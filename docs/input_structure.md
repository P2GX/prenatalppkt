# Input Format Crosswalk: Observer JSON, ViewPoint Text, and ViewPoint HL7

## 1. Overview of Input Formats

### 1.1 Observer JSON Export
**Structure**: Hierarchical JSON with nested objects representing the complete exam structure.
```
exam
  - patient, ob_gyn_history, exam metadata
- fetuses[]
  - fetus (core data: fetus_number, presentation, gender)
  - measurements[] (AC, BPD, HC, FL with percentiles)
  - efws[] (EFW calculations with percentiles)
  - ratios[] (HC/AC, FL/BPD, etc.)
  - anatomy[] (structured anatomy findings)
  - fetalvessels (doppler data)
  - impression (fetus_anomalies[])
  - other blocks (placenta, amniotic fluid, etc.)
```

**Units**: Predominantly centimeters (cm) for linear measurements, grams (g) for weight.

**Percentiles**: Stored as `calculated_percentile` (numeric) and `percentile_for_display` (formatted string with %).

### 1.2 ViewPoint Text Export
**Structure**: Plain text with section headers delimited by equals signs (========).
```
Indication
========
[clinical reason ingtext]

History
======
[OB history details]

Fetal Biometry
============
BPD    76.6    mm    30w 5d    <1%    Hadlock
HC     285.7   mm    30w 4d    <1%    Chervenak
...

General Evaluation
==============
[narrative text]

Fetal Anatomy
===========
[normal/abnormal/not visualized lists]

Fetal Doppler
===========
[doppler measurements]
```

**Units**: Millimeters (mm) for linear measurements, grams (g) for weight.

**Percentiles**: Inline strings like "55%", "<1%", ">99%".

### 1.3 ViewPoint Discrete HL7 (ORU^R01)
**Structure**: HL7 v2.4 message with OBX segments encoding each measurement and metadata field.
```
MSH|...
PID|...
OBR|...
OBX|57|NM|AbdomenFetus.AbdominalCircumference^AC^Abdominal circumference|Fetus1|56^56.0|mm&millimeters^mm&millimeters|...
OBX|61|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|73^73%|%&percent^fmt&formatted|...
OBX|60|NM|AbdomenFetus.VP_AbdominalCircumference_Deviation|Fetus1|0.6^+0.6SD|sd&standard deviation^fmt&formatted|...
```

**Units**: Millimeters (mm) encoded as `mm&millimeters^mm&millimeters`.

**Percentiles**: Separate OBX segments for raw value, GA, percentile, z-score, and deviation ratio.

---

## 2. Biometry Measurement Crosswalk

### 2.1 Mapping Table

| Measurement | Observer JSON | ViewPoint Text | ViewPoint HL7 | term_bin Input |
|-------------|--------------|----------------|---------------|----------------|
| **BPD** (Biparietal Diameter) | `fetuses[i].measurements[]` where `label="BPD"`, `value` in cm, `calculated_percentile` | Line starting with "BPD", space-delimited: value(mm), unit, GA, percentile%, method | `SkullFetus.BiParietalDiameter` (value in mm), `VP_BiParietalDiameter_Percentile` | `value`, `percentile` -> `PercentileRange.evaluate()` |
| **HC** (Head Circumference) | `fetuses[i].measurements[]` where `label="HC"`, `value` in cm, `calculated_percentile` | Line starting with "HC", space-delimited: value(mm), unit, GA, percentile%, method | `SkullFetus.HeadCircumference` (value in mm), `VP_HeadCircumference_Percentile` | `value`, `percentile` -> `PercentileRange.evaluate()` |
| **AC** (Abdominal Circumference) | `fetuses[i].measurements[]` where `label="AC"`, `value` in cm, `calculated_percentile` | Line starting with "AC", space-delimited: value(mm), unit, GA, percentile%, method | `AbdomenFetus.AbdominalCircumference` (value in mm), `VP_AbdominalCircumference_Percentile` | `value`, `percentile` -> `PercentileRange.evaluate()` |
| **FL** (Femur Length) | `fetuses[i].measurements[]` where `label="Femur"`, `value` in cm, `calculated_percentile` | Line starting with "Femur", space-delimited: value(mm), unit, GA, percentile%, method | `ExtremitiesFetus.FemurUndefinedLength` (value in mm), `VP_FemurUndefinedLength_Percentile` | `value`, `percentile` -> `PercentileRange.evaluate()` |
| **OFD** (Occipito-Frontal Diameter) | Not present in sample | Line starting with "OFD", space-delimited: value(mm), unit, GA, percentile%, method | Not present in sample | `value`, `percentile` -> `PercentileRange.evaluate()` |

### 2.2 Example: BPD Across Formats

**Observer JSON** (`Apple_Sally_pretty.json`):
```json
{
  "label": "BPD",
  "value": 6.68,
  "decimal_places": 2,
  "unit_of_measure": "cm",
  "calculated_ega": 26.9,
  "calculated_percentile": 51.2,
  "percentile_for_display": "51%",
  "include_in_avg_ga_calc": 1,
  "print_in_report": 1,
  "calculated_z_score": 0,
  "fetus_number": 1
}
```

**ViewPoint Text** (`viewpoint_text_1-8.txt`):
```
BPD                                                         76.6                    mm                         30w 5d                     <1%                    Hadlock
```
Parsed components: `['BPD', '76.6', 'mm', '30w', '5d', '<1%', 'Hadlock']`

**ViewPoint HL7** (`Discrete_HL7_Messages_Sample.txt`):
```
OBX|69|NM|EmbryonicStructuresFetus.CrownRumpLength^CRL^Crown rump length|Fetus1|55^55.0|mm&millimeters^mm&millimeters||||||||20211223144928
OBX|73|NM|EmbryonicStructuresFetus.VP_CrownRumpLength_Percentile|Fetus1|31^31%|%&percent^fmt&formatted||||||||20211223144928
```
(Note: HL7 sample shows CRL; BPD follows same pattern)

**term_bin Mapping**:
```python
# From any format, extract:
value_mm = 76.6  # or convert from cm
percentile_str = "<1%"
percentile_value = parse_percentile(percentile_str)  # -> 0.5 or similar

perc_range = PercentileRange.evaluate(percentile_value)
# -> PercentileRange.below_3p() if percentile < 3

term_bin = TermBin.from_term(
  range=perc_range,
  term=DECREASED_BPD_TERM,  # if abnormal
  normal=False,
  description=f"{value_mm} mm {percentile_str} at G30w5d (Hadlock)"
)
```

### 2.3 Unit Conversion Requirements

| Format | Linear Units | Weight Units | Conversion to term_bin |
|--------|--------------|--------------|------------------------|
| Observer JSON | cm | g | Multiply by 10 for mm |
| ViewPoint Text | mm | g | Use directly |
| ViewPoint HL7 | mm | g | Use directly |

---

## 3. Estimated Fetal Weight (EFW) Crosswalk

### 3.1 EFW Mapping Table

| Aspect | Observer JSON | ViewPoint Text | ViewPoint HL7 | term_bin Input |
|--------|---------------|----------------|---------------|----------------|
| **EFW Value** | `fetuses[i].efws[]` where `label` contains "EFW", `value` in grams | "EFW" line: value, unit (g), percentile% | Not present in sample (would be similar pattern) | `value`, `percentile` |
| **Method** | `label` specifies formula (e.g., "EFW (AC, FL, HC)") | "EFW by" line: method name | Would be in component name | Stored in description |
| **Percentile** | `calculated_percentile`, `percentile_for_display` | Inline percentile string | Separate OBX segment | Maps to `PercentileRange` |

### 3.2 Example: EFW Across Formats

**Observer JSON**:
```json
{
  "fetus_number": 1,
  "label": "EFW (AC, FL, HC)",
  "value": 1014.828,
  "decimal_paces": 0,
  "calculated_percentile": 55.6,
  "percentile_for_display": "56%",
  "print_in_report": 1,
  "range": ""
}
```

**ViewPoint Text**:
```
EFW                                                        2,042                  g                                                             2%
EFW (lb,oz)                                              4 lb 8                  oz
EFW by                                                     Hadlock (BPD-HC-AC-FL)
```

**term_bin Mapping**:
```python
efw_grams = 2042
percentile = 2.0

perc_range = PercentileRange.evaluate(percentile)  # -> below_3p()

# Map to growth restriction term if below threshold
if perc_range <= DEFAULT_EFW_LOW:
  term = FETAL_GROWTH_RESTRICTION_TERM
  normal = False
else:
  term = NORMAL_EFW_TERM
  normal = True

term_bin = TermBin.from_term(
  range=perc_range,
  term=term,
  normal=normal,
  description=f"EFW {efw_grams}g at 2% (Hadlock BPD-HC-AC-FL)"
)
```

---

## 4. Ratio Crosswalk

### 4.1 Ratio Mapping Table

| Ratio | Observer JSON | ViewPoint Text | ViewPoint HL7 | term_bin Input |
|-------|---------------|----------------|---------------|----------------|
| **HC/AC** | `fetuses[i].ratios[]` where `label="HC/AC"`, `value`, `range` string | "FL / HC" section under biometry (note: sometimes inverted) | Would follow measurement pattern | `value`, optional `range` |
| **FL/BPD** | `fetuses[i].ratios[]` where `label="FL/BPD"`, `value`, `range` string | Not always present in text | Would follow measurement pattern | `value`, optional `range` |
| **FL/AC** | `fetuses[i].ratios[]` where `label="FL/AC"`, `value`, `range` string | Not always present in text | Would follow measurement pattern | `value`, optional `range` |

### 4.2 Example: HC/AC Ratio

**Observer JSON**:
```json
{
  "label": "HC/AC",
  "value": 1.105,
  "decimal_paces": 2,
  "calculated_percentile": 0,
  "percentile_for_display": "",
  "print_in_report": 1,
  "range": "1.04 - 1.22",
  "fetus_number": 1
}
```

**ViewPoint Text**:
```
FL / HC                                                    0.23
```
(Note: Text shows FL/HC = 0.23, which is inverse of HC/FL = 4.35)

**term_bin Mapping**:
```python
# Ratios typically don't map to HPO terms directly
# But can be used to assess proportionality

hc_ac_ratio = 1.105
expected_range = (1.04, 1.22)

if expected_range[0] <= hc_ac_ratio <= expected_range[1]:
  normal = True
  term = NORMAL_PROPORTIONS_TERM
else:
  normal = False
  term = ABNORMAL_PROPORTIONS_TERM

# Usually stored as metadata rather than term_bin
```

---

## 5. Fetus Identity Crosswalk

### 5.1 Fetus Numbering

| Aspect | Observer JSON | ViewPoint Text | ViewPoint HL7 |
|--------|---------------|----------------|---------------|
| **Fetus Count** | `exam.fetus_count` (integer) | "Singleton pregnancy. Number of fetuses: 1" | `EpisodeHistory.NumberOfFetuses` OBX |
| **Fetus Index** | `fetuses[i].fetus.fetus_number` (1-based) | Implicit (usually single fetus) | Pipe-delimited position: `\|Fetus1\|` |
| **Multiple Fetuses** | Array: `fetuses[0]`, `fetuses[1]`, etc. | Separate reports or sections | `Fetus1`, `Fetus2` in observation identifier |

### 5.2 Example: Singleton vs Twin

**Observer JSON** (Singleton):
```json
{
  "exam": {
    "fetus_count": 1,
    ...
  },
  "fetuses": [
    {
      "fetus": {
        "fetus_number": 1,
      ...
      }
    }
  ]
}
```

**ViewPoint Text** (Singleton):
```
Pregnancy
=========

Singleton pregnancy. Number of fetuses: 1
```

**ViewPoint HL7**:
```
OBX|22|ST|EpisodeHistory.NumberOfFetuses^Number of gestational sacs/ fetuses/ babies^...|1|...
OBX|56|ST|Fetus.Identifier^Fetus Identifier^Fetus Identifier|Fetus1|A|...
```

**Parser Strategy**:
- Observer: Iterate `fetuses[]` array
- ViewPoint Text: Parse "Number of fetuses: N" from Pregnancy section
- HL7: Extract fetus identifier from observation identifier field

---

## 6. Narrative Fields Crosswalk

### 6.1 Clinical Impression / Narrative

| Field | Observer JSON | ViewPoint Text | ViewPoint HL7 |
|-------|---------------|----------------|---------------|
| **Clinical Impression** | `fetuses[i].fetus.impression_text` | Section "Impression" with paragraph text | `RequestedProcedure.RelevantClinicalInfo` (partial) |
| **Anatomy Text** | `fetuses[i].fetus.anatomy_text` | Section "Fetal Anatomy" with free text | Not directly encoded |
| **General Comment** | `finalize.generalComment.plain_text` | Paragraph text in Impression section | Not directly encoded |

### 6.2 Structured Anatomy Data

| Aspect | Observer JSON | ViewPoint Text | ViewPoint HL7 |
|--------|---------------|----------------|---------------|
| **Anatomy Structure** | `fetuses[i].anatomy[]` with `main.label`, `main.anat_state` | Bulleted lists: "appear normal", "appear abnormal", "not visualized" | Not present in sample |
| **Abnormality Details** | `anatomy[].anomalies[]` with `description` | Inline text or separate anomaly lines | Not present in sample |
| **HPO Mapping** | Manual mapping from `description` | Parse from free text using HPO recognizer | N/A |

### 6.3 Example: Anatomy Findings

**Observer JSON**:
```json
{
  "main": {
    "label": "Head",
    "anat_state": "Abnormal",
    "print_in_report": 1,
    "main_txt": "Abnormalities in the head were noted...",
    "required": "Yes"
  },
  "detail": [
    {
      "label": "Cerebellum",
      "anat_det_state": "Abnormal",
      "print_in_report": 1
    }
  ],
  "anomalies": [
    {
      "abnormal_or_normal_variant": "Abnormal",
      "description": "Dandy Walker"
    }
  ]
}
```

**ViewPoint Text**:
```
Fetal Anatomy
===========

The following structures appear abnormal:
GI tract: dilated bowel loops.

The following structures appear normal:
Cranium. Brain. Face. Situs. Cardiac rhythm. 4-chamber view. ...

The following structures could not be adequately visualized:
LVOT view. RVOT view. Spine. Arms. Legs.
```

**term_bin Mapping**:
```python
# Parse anatomy state
if "Dandy Walker" in anomaly_description:
  # Search HPO for matching term
  term = hpo_cr.find_concepts("Dandy Walker")
  # -> HP:0001305 "Dandy-Walker malformation"
   
  term_bin = TermBin.from_term(
    range=None,  # qualitative finding
    term=term,
    normal=False,
    description="Dandy Walker malformation identified on ultrasound"
  )
```

---

## 7. Doppler Crosswalk

### 7.1 Doppler Measurement Mapping

| Measurement | Observer JSON | ViewPoint Text | ViewPoint HL7 | term_bin Input |
|-------------|---------------|----------------|---------------|----------------|
| **UA PI** (Umbilical Artery Pulsatility Index) | `fetuses[i].fetalvessels.umbilical_artery.pulsatility_index`, `pulsatility_index_percentile` | "Umbilical Artery:" section, "PI" line with value and percentile | Would follow OBX pattern | `value`, `percentile` -> `PercentileRange` |
| **UA RI** (Resistance Index) | `fetalvessels.umbilical_artery.resistance_index`, `resistance_index_percentile` | "RI" line with value and percentile | Would follow OBX pattern | `value`, `percentile` |
| **UA S/D** (Systolic/Diastolic Ratio) | `fetalvessels.umbilical_artery.systolic_diastolic_ratio`, `systolic_diastolic_ratio_percentile` | "S / D" line with value and percentile | Would follow OBX pattern | `value`, `percentile` |
| **MCA PSV** (Middle Cerebral Artery Peak Systolic Velocity) | `fetalvessels.middle_cerebral_artery.peak_systolic_velocity`, `peak_systolic_velocity_percentile` | "Mid Cerebral Artery:" section, "PS" line | Would follow OBX pattern | `value`, `percentile`, MoM |
| **MCA PI** | `fetalvessels.middle_cerebral_artery.pulsatility_index`, `pulsatility_index_percentile` | "PI" line with value and percentile | Would follow OBX pattern | `value`, `percentile` |
| **CPR** (Cerebroplacental Ratio) | Not in sample (would be calculated) | "CPR PI" line with value and percentile | Would follow OBX pattern | `value`, `percentile` |

### 7.2 Example: Umbilical Artery Doppler

**Observer JSON** (not present in sample, typical structure):
```json
{
  "umbilical_artery": {
    "done": 1,
    "pulsatility_index": 1.15,
    "pulsatility_index_percentile": 96.0,
    "resistance_index": 0.69,
    "resistance_index_percentile": 87.0,
    "systolic_diastolic_ratio": 3.31,
    "systolic_diastolic_ratio_percentile": 91.0,
    "absent_end_diastolic_velocity": "No",
    "reverse_flow": "No"
  }
}
```

**ViewPoint Text**:
```
Fetal Doppler
===========

Umbilical Artery:
PI                                                             1.15                                                                                  96%                     Baschat
RI                                                             0.69                                                                                  87%                     Schaffer
PS                                                           -48.74                 cm/s
ED                                                           -15.48                 cm/s
S / D                                                        3.31                                                                                   91%                    Acharya
```

**term_bin Mapping**:
```python
ua_pi = 1.15
ua_pi_percentile = 96.0

perc_range = PercentileRange.evaluate(ua_pi_percentile)
# -> above_95p() or p90_to_p95()

if perc_range >= DEFAULT_UA_PI_HIGH:
  term = INCREASED_UA_PI_TERM  # indicates possible placental insufficiency
  normal = False
elif perc_range <= DEFAULT_UA_PI_LOW:
  term = DECREASED_UA_PI_TERM
  normal = False
else:
  term = NORMAL_UA_PI_TERM
  normal = True

term_bin = TermBin.from_term(
  range=perc_range,
  term=term,
  normal=normal,
  description=f"UA PI {ua_pi} at 96% (Baschat)"
)
```

### 7.3 Qualitative Doppler Findings

| Finding | Observer JSON | ViewPoint Text | term_bin Mapping |
|---------|---------------|----------------|------------------|
| **Absent End-Diastolic Velocity** | `absent_end_diastolic_velocity: "Yes"` | "AEDV" or text: "ABNORMAL with DECREASED end diastolic flow" | Maps to HP term for AEDV |
| **Reverse Flow** | `reverse_flow: "Yes"` | Text: "reverse flow noted" | Maps to HP term for reverse flow |
| **Normal Doppler** | `done: 1`, normal values | Text: "within normal limits for this gestational age" | No term_bin (normal) |

---

## 8. term_bin Mapping Strategy

### 8.1 Percentile Range Bins

All three input formats must normalize percentiles into these standard bins:

| Bin | Percentile Range | PercentileRange Value | Clinical Interpretation |
|-----|------------------|----------------------|-------------------------|
| Below 3rd | < 3% | `PercentileRange.below_3p()` | Severely decreased |
| 3rd to 5th | 3% - <5% | `PercentileRange.p3_to_p5()` | Moderately decreased |
| 5th to 10th | 5% - <10% | `PercentileRange.p5_to_p10()` | Mildly decreased |
| 10th to 50th | 10% - <50% | `PercentileRange.p10_to_p50()` | Low normal |
| 50th to 90th | 50% - <90% | `PercentileRange.p50_to_p90()` | Normal |
| 90th to 95th | 90% - <95% | `PercentileRange.p90_to_p95()` | Mildly increased |
| 95th to 97th | 95% - <97% | `PercentileRange.p95_to_p97()` | Moderately increased |
| Above 97th | >= 97% | `PercentileRange.above_97p()` | Severely increased |

### 8.2 Special Percentile Strings

| String | Observer JSON | ViewPoint Text | HL7 | Mapping |
|--------|---------------|----------------|-----|---------|
| Below 1st | N/A (would be 0 or <1) | `<1%` | `<1%` | `PercentileRange.below_3p()` |
| Above 99th | N/A (would be 99.x) | `>99%` | `>99%` | `PercentileRange.above_97p()` |
| Exact values | `51.2` | `51%` | `51^51%` | `PercentileRange.evaluate(51.2)` |

### 8.3 Universal Parser Pattern
```python
def normalize_to_term_bin( measurement_name: str, value: float, percentile: Union[float, str], unit: str, gestational_age: str, method: str) -> TermBin:
  """
  Universal function to convert any measurement from any format
  into a standardized TermBin object.

  Works for Observer JSON, ViewPoint Text, or HL7.
  """
  # 1. Parse percentile string if needed
  if isinstance(percentile, str): percentile = parse_percentile_string(percentile)

  # 2. Convert units if needed
  if unit == "cm" and measurement_name in ["BPD", "HC", "AC", "FL"]: value_mm = value * 10
  else: value_mm = value

  # 3. Map to percentile range
  perc_range = PercentileRange.evaluate(percentile)

  # 4. Determine if normal and select appropriate term
  normal, hpo_term = select_term_for_measurement(measurement_name, perc_range)

  # 5. Create description
  description = f"{value_mm} mm ({percentile}%) at {gestational_age} ({method})"

  # 6. Return TermBin
  return TermBin.from_term(range=perc_range, term=hpo_term, normal=normal, description=description)
```

### 8.4 Format-Specific Parsing

**Observer JSON**:
```python
for measurement in fetuses[0]["measurements"]:
  term_bin = normalize_to_term_bin(
    measurement_name=measurement["label"],
    value=measurement["value"],
    percentile=measurement["calculated_percentile"],
    unit=measurement["unit_of_measure"],
    gestational_age=f"{measurement['calculated_ega']}w",
    method="Observer"  # method not directly stored
  )
```

**ViewPoint Text**:
```python
# Parse biometry line
parts = line.split()  # ['BPD', '76.6', 'mm', '30w', '5d', '<1%', 'Hadlock']

term_bin = normalize_to_term_bin(
  measurement_name=parts[0],
  value=float(parts[1]),
  percentile=parts[5],
  unit=parts[2],
  gestational_age=f"{parts[3]}{parts[4]}",
  method=parts[6]
)
```

**ViewPoint HL7**:
```python
# Extract from OBX segments
value_obx = parse_obx("AbdomenFetus.AbdominalCircumference")
percentile_obx = parse_obx("AbdomenFetus.VP_AbdominalCircumference_Percentile")
ga_obx = parse_obx("AbdomenFetus.VP_AbdominalCircumference_GA")
method_obx = parse_obx("AbdomenFetus.VP_AbdominalCircumference_Author")

term_bin = normalize_to_term_bin(
  measurement_name="AC",
  value=value_obx["value"],
  percentile=percentile_obx["value"],
  unit="mm",
  gestational_age=ga_obx["value"],
  method=method_obx["value"]
)
```

---

## 9. Open Questions and Ambiguities

### 9.1 Unit Inconsistencies

**Issue**: Observer JSON uses cm while ViewPoint uses mm for the same measurements.

**Resolution**: All parsers must convert to a common unit (mm recommended) before creating term_bins.

**Status**: Conversion factor is 10x, straightforward to implement.

### 9.2 Method/Reference Differences

**Issue**: Different growth charts may be used:
- Observer: Method not always explicitly stated
- ViewPoint Text: Hadlock, Nicolaides, Chervenak, Baschat, etc.
- HL7: Same as text, in separate OBX

**Resolution**: Store method in term_bin description; may need method-specific percentile tables.

**Status**: Current implementation uses generic percentile bins regardless of method.

### 9.3 Missing Data in HL7 Sample

**Issue**: The provided HL7 sample (`Discrete_HL7_Messages_Sample.txt`) is from a first trimester exam and lacks:
- BPD, HC, AC measurements (only CRL, AC, FHR, FL)
- EFW calculations
- Doppler measurements
- Fetal anatomy details

**Resolution**: Extrapolate structure from what's present (pattern is consistent).

**Status**: Assumed structure documented above; needs validation with full HL7 export.

### 9.4 Ratio Interpretation

**Issue**: Ratios don't always have percentiles in all formats.

**Resolution**: Store ratios with expected normal ranges; compare value to range rather than using percentile bins.

**Status**: Ratios are informational; not always mapped to term_bins.

### 9.5 Multiple Fetuses

**Issue**: ViewPoint text exports may handle twins differently (separate reports vs. inline).

**Resolution**: Parser must detect fetus count and handle accordingly.

**Status**: Current parsers assume singleton; multi-fetus support needs testing.

### 9.6 Doppler Qualitative vs Quantitative

**Issue**: Some doppler findings are qualitative (AEDV present/absent) while others are quantitative (PI value).

**Resolution**:
- Quantitative: Use percentile bins as with biometry
- Qualitative: Direct HPO term mapping (e.g., AEDV -> HP:0025634)

**Status**: Qualitative mapping not yet fully implemented.

### 9.7 Anatomy Text Parsing

**Issue**: Free text anatomy descriptions require NLP/HPO concept recognition.

**Resolution**: Use `hpo_cr` (HPO concept recognizer) to extract terms from:
- Observer: `anatomy_text`, `impression_text`, anomaly descriptions
- ViewPoint: Impression section, anatomy comments
- HL7: Not applicable (anatomy not encoded in discrete fields in sample)

**Status**: HPO CR integration exists for ViewPoint impression parser; needs expansion.

### 9.8 Gestational Age Representation

**Issue**: Multiple GA formats across systems:
- Observer: `calculated_ega: 26.9` (weeks as decimal)
- ViewPoint: `30w 5d` (weeks + days string)
- HL7: `85^12w 1d|d&weeks_days^fmt&formatted` (days + formatted string)

**Resolution**: Normalize all to `GestationalAge` class with `weeks` and `days` properties.

**Status**: `GestationalAge` class exists; parsers must use it consistently.

---

## 10. Implementation Checklist

### 10.1 Parser Requirements

- [ ] Observer JSON parser extracts all measurements into common format
- [ ] ViewPoint text parser handles all biometry lines
- [ ] HL7 parser clusters related OBX segments for each measurement
- [ ] All parsers normalize units to mm/g
- [ ] All parsers convert percentiles to `PercentileRange` enum
- [ ] All parsers create `TermBin` objects with consistent structure

### 10.2 Data Quality Checks

- [ ] Validate percentile values are in [0, 100] range
- [ ] Detect and flag special percentile strings (`<1%`, `>99%`)
- [ ] Ensure measurement values are positive
- [ ] Check for missing required fields (value, percentile, fetus number)
- [ ] Validate GA is reasonable (e.g., 10-42 weeks)

### 10.3 Test Coverage

- [ ] Unit tests for each parser with sample data
- [ ] Integration tests converting all three formats to term_bins
- [ ] Comparison tests ensuring equivalent measurements map to same bins
- [ ] Edge case tests (extreme percentiles, missing data, multiple fetuses)

### 10.4 Documentation

- [x] This crosswalk document completed
- [ ] Individual parser docstrings reference this crosswalk
- [ ] README updated with format support matrix
- [ ] Examples added to docs/ showing end-to-end conversion

---

## Appendix A: Field Name Reference

### A.1 Observer JSON Paths
```
exam.fetus_count                          -> number of fetuses
exam.ga_by_working_edd                    -> gestational age (weeks, decimal)
fetuses[i].fetus.fetus_number             -> fetus index (1-based)
fetuses[i].fetus.gender                   -> fetal sex
fetuses[i].fetus.heart_bpm                -> fetal heart rate
fetuses[i].fetus.impression_text          -> clinical impression
fetuses[i].fetus.anatomy_text             -> anatomy narrative
fetuses[i].measurements[]                 -> biometry array
  .label                                  -> measurement name (BPD, HC, AC, FL, etc.)
  .value                                  -> measurement value (cm)
  .unit_of_measure                        -> "cm", "mm", "g"
  .calculated_percentile                  -> percentile (0-100)
  .percentile_for_display                 -> formatted string
  .calculated_ega                         -> GA by this measurement
fetuses[i].efws[]                         -> EFW calculations
  .label                                  -> formula description
  .value                                  -> weight in grams
  .calculated_percentile                  -> percentile
fetuses[i].ratios[]                       -> fetal ratios
  .label                                  -> ratio name (HC/AC, FL/BPD, etc.)
  .value                                  -> ratio value
  .range                                  -> expected normal range string
fetuses[i].anatomy[]                      -> structured anatomy
  .main.label                             -> anatomy region
  .main.anat_state                        -> Normal/Abnormal/Unseen
  .anomalies[].description                -> specific finding
fetuses[i].fetalvessels                   -> doppler measurements
  .umbilical_artery.pulsatility_index     -> UA PI
  .middle_cerebral_artery.peak_systolic_velocity -> MCA PSV
```

### A.2 ViewPoint Text Section Headers
```
Indication                    -> Clinical reason for exam
History                       -> OB history, gravida/para
Method                        -> Equipment and approach
Pregnancy                     -> Singleton/twin, number of fetuses
Dating                        -> GA calculation table
Fetal Growth Overview         -> Growth curve table
Fetal Biometry                -> Biometry measurements with percentiles
General Evaluation            -> FHR, presentation, fluid, cord
Fetal Anatomy                 -> Normal/abnormal/not visualized lists
Fetal Doppler                 -> Doppler measurements by vessel
Impression                    -> Clinical summary and interpretation
Follow-up                     -> Recommendations
```

### A.3 ViewPoint HL7 Component Names
```
EpisodeHistory.NumberOfFetuses              -> fetus count
Fetus.Identifier                            -> Fetus1, Fetus2, etc.

AbdomenFetus.AbdominalCircumference         -> AC value (mm)
VP_AbdominalCircumference_Percentile        -> AC percentile
VP_AbdominalCircumference_GA                -> GA by AC
VP_AbdominalCircumference_Deviation         -> z-score

SkullFetus.HeadCircumference                -> HC value (mm)
VP_HeadCircumference_Percentile             -> HC percentile

ExtremitiesFetus.FemurUndefinedLength       -> FL value (mm)
VP_FemurUndefinedLength_Percentile          -> FL percentile

HeartFetus.FetalHeartRate                   -> FHR (bpm)
VP_FetalHeartRate_Percentile                -> FHR percentile
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-17  
**Maintained By**: prenatalppkt development team  
**Purpose**: Guide parser development and ensure consistent term_bin generation across all input formats