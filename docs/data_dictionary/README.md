# prenatalppkt data dictionary

Cross-source field inventory for the prenatalppkt ETL. Every leaf path in the CUIMC Observer JSON corpus and every OBX-3 identifier in the EVMS GE HL7 v2.4 corpus appears here, grouped into clinical clusters, with Observer rows split per measurement label and Observer + HL7 fields paired on the same row whenever a label token and value class match.

`docs/data_dictionary/comparison.csv` is the canonical artifact (1512 rows: 1170 carry an Observer field, 374 carry an HL7 field, 32 pair both on one row). These docs are generated from it; edit `render_readme.py`, `extract_all.py`, `clusters.yaml`, or `concept_aliases.yaml`, never the generated docs themselves.

## For clinicians: cross-source field map

Plain-language map of the data this pipeline ingests.

### What the two sources are

**Observer JSON** (CUIMC). A structured per-exam record exported by Columbia's prenatal-imaging system. Organized by fetus, with measurements, anatomy findings, and impressions stored as nested fields inside a single JSON file per exam. Strong on free-text narrative and multi-fetus structure; weaker on standardized HL7 codes.

**ViewPoint HL7** (EVMS, via GE). An HL7 v2.4 message stream exported from EVMS's GE ViewPoint system. Each finding is one OBX line with a system-specific field identifier (e.g. `SkullFetus.BiparietalDiameter`), a short label (e.g. `BPD`), and a value. Strong on standardized field naming; weaker on multi-fetus disambiguation and on free-text narrative.

### Concepts both systems capture (or only one side does)

The 22 hand-curated concepts in `concept_aliases.yaml`, sorted by clinical area. `(Observer-only)` / `(ViewPoint-only)` mark where only one source has the field.

| Concept | Clinical area | Observer field | ViewPoint field | Type | Example |
| --- | --- | --- | --- | --- | --- |
| Abdominal circumference, raw measurement in mm | biometry | `fetuses[].measurements[].value @ AC` | `AbdomenFetus.AbdominalCircumference` | number | 26.9 |
| Abdominal circumference percentile vs gestational age | biometry | `fetuses[].measurements[].calculated_percentile @ AC` | (Observer-only) | number | 55.6 |
| Biparietal diameter, raw measurement in mm | biometry | `fetuses[].measurements[].value @ BPD` | `SkullFetus.BiparietalDiameter` | number | 26.9 |
| Biparietal diameter percentile vs gestational age | biometry | `fetuses[].measurements[].calculated_percentile @ BPD` | `Fetus.BPD%` | number | 51.2 |
| Crown-rump length, raw measurement in mm (first-trimester) | biometry | `fetuses[].measurements[].value @ CRL` | `EmbryonicStructuresFetus.CrownRumpLength` | number | 11.3 |
| Crown-rump length percentile | biometry | `fetuses[].measurements[].calculated_percentile @ CRL` | (Observer-only) | number | 0 |
| Femur length, raw measurement in mm | biometry | `fetuses[].measurements[].value @ Femur` | `ExtremitiesFetus.FemurUndefinedLength` | number | 27.1 |
| Femur length percentile vs gestational age | biometry | `fetuses[].measurements[].calculated_percentile @ Femur` | (Observer-only) | number | 46.8 |
| Head circumference, raw measurement in mm | biometry | `fetuses[].measurements[].value @ HC` | `SkullFetus.HeadCircumference` | number | 26.9 |
| Head circumference percentile vs gestational age | biometry | `fetuses[].measurements[].calculated_percentile @ HC` | (Observer-only) | number | 42.5 |
| Humerus length, raw measurement in mm | biometry | `fetuses[].measurements[].value @ Humerus` | `ExtremitiesFetus.HumerusLength` | number | 3.9 |
| Humerus length percentile vs gestational age | biometry | `fetuses[].measurements[].calculated_percentile @ Humerus` | (Observer-only) | number | 49.2 |
| Nuchal fold thickness, raw measurement in mm | biometry | `fetuses[].measurements[].value @ Nuchal Fold` | `NeckSkinFetus.NuchalFold` | number | 1 |
| Nuchal fold thickness percentile | biometry | `fetuses[].measurements[].calculated_percentile @ Nuchal Fold` | (Observer-only) | number | 0 |
| Cervix funneling presence | cervix | `cervix.cervix.funneling` | `Cervix.FunnellingYN` | coded | Unspecified |
| Fetal sex | fetus | `fetuses[].fetus.gender` | `BabyPatientData.Gender` | coded | Unspecified |
| ICD-10 indication code | indication | `exam.examIcd10Indication[].code` | `CodingDiagnosis.Code` | coded | Z36.1 |
| ICD-10 indication description / narrative | indication | `exam.examIcd10Indication[].description` | `CodingDiagnosis.Description` | coded | Encounter for antenatal screening for raised alphafetoprotein level |
| Patient first name | maternal | `exam.patient.first_name` | `PatientHistory.FirstName` | coded | Sally |
| Gravidity (count of pregnancies including current) | maternal | `exam.ob_gyn_history.gravida` | `PatientAnamnesticData.Gravida` | number | 0 |
| Patient last name / family name | maternal | `exam.patient.last_name` | `PatientHistory.Name` | coded | Apple |
| Parity (count of completed pregnancies past 20 weeks) | maternal | `exam.ob_gyn_history.para` | `PatientAnamnesticData.Para` | number | 0 |

### Where the two sources diverge (by clinical area)

For each clinical area, how many fields each source has and what that means for an XLSX template. `Observer-only` counts include rows where Observer has data but no HL7 counterpart fired; `ViewPoint-only` is the converse. `Paired` is the count where both sides land on the same row.

| Clinical area | Observer-only | ViewPoint-only | Paired | What this means for the XLSX |
| --- | --- | --- | --- | --- |
| biometry | 137 | 100 | 12 | Both systems capture the core biometry suite (BPD, AC, HC, CRL, Femur, Humerus, Nuchal Fold) as numbers in mm. ViewPoint reports one HL7 field per measurement; Observer stores them as a list tagged by `label`. The XLSX should have one row per measurement with a number column for the raw value and a percentile column. |
| anatomy_brain | 0 | 14 | 0 | ViewPoint has a discrete `BrainFetus.*` HL7 namespace (ventricles, cerebellum, choroid plexus, posterior fossa). Observer captures the same findings inside free-text `fetuses[].anatomy[].*.brain` fields. The XLSX should pre-define brain anatomy fields so the receiving center isn't forced to free-type them. |
| anatomy_face_neck | 0 | 3 | 0 | ViewPoint has `FaceFetus.*`; Observer keeps these as free-text anatomy entries. Pre-define orbits, lips, palate, profile, neck fields in the XLSX. |
| anatomy_chest_gi | 0 | 12 | 0 | ViewPoint splits chest (non-cardiac) and GI into discrete fields; Observer lumps them into anatomy free text. Pre-define discrete chest + GI anatomy fields in the XLSX. |
| anatomy_spine | 0 | 1 | 0 | ViewPoint has `SpineFetus.*`; Observer keeps spine findings under free-text anatomy. The XLSX should pre-define spine fields. |
| anatomy_urinary | 0 | 46 | 0 | ViewPoint has `UrinaryTractFetus.*` (kidneys, bladder, ureters); Observer mostly free-text. Pre-define the urinary fields in the XLSX. |
| anatomy_general | 295 | 0 | 0 | Observer-only structural anatomy wrappers. ViewPoint has no equivalent namespace. The XLSX should provide a wide free-text column for system-agnostic anatomy notes. |
| cardiac | 231 | 63 | 12 | Both systems carry detailed cardiac findings and echocardiography measurements. The XLSX should accommodate both discrete cardiac-anatomy fields and free-text echocardiography findings. |
| amniotic_fluid | 9 | 7 | 0 | Both systems carry amniotic-fluid index and deepest-pocket. Numbers in cm. The XLSX should have AFI and SDP numeric columns plus a categorical (oligo / normal / polyhydramnios). |
| placenta_cord | 119 | 32 | 0 | Both systems cover placenta + cord findings but tokenize differently (Observer's `cord.numberOfVessels` vs ViewPoint's `Cord.VesselCount`). The XLSX should include both naming styles as alias columns until a concept alias is hand-curated. |
| fetal_procedures | 41 | 0 | 0 | Observer-only invasive procedures (amniocentesis, CVS/FBS, ectopic mgmt). The XLSX should provide a procedure-type column plus a free-text findings column. |
| fetus_core | 33 | 3 | 1 | Both systems carry per-fetus identity (fetal sex, presentation, movements, tone). Fetal sex maps directly to a coded enum. The XLSX should have one row per fetus with these as columns. |
| indication_impression | 0 | 6 | 2 | Both systems carry ICD-10 indication codes + descriptions. Coded in both. The XLSX should have an indication-code column (ICD-10 format) and a free-text impression column. |
| dating | 5 | 12 | 0 | Both systems carry pregnancy dating: LMP, EDD, gestational age, agreed dating string. They tokenize differently (Observer's `ga_by_dates` vs ViewPoint's `ExamOBDating.*`). The XLSX should have LMP, EDD, GA-at-exam, and dating-method columns. |
| maternal_subject | 23 | 7 | 4 | Both systems carry maternal demographics + obstetric history (gravida, para, name, age). Coded in both. The XLSX should have a maternal header block with these as standard columns. |
| encounter | 21 | 33 | 0 | Exam-level metadata: date, location, signing, exam type, referring provider, accession. ViewPoint has structured `Exam.*` + `ExamAddData.*`; Observer scatters this under `exam.*` keys. The XLSX should pre-define encounter metadata as a header block. |
| non_fetal_gyn | 224 | 3 | 1 | Mostly Observer-only gynecologic findings (adnexa, cervix, uterine artery, gyn procedures). Cervix funneling is the one concept paired across sources. The XLSX should provide a free-text gyn-findings block plus discrete cervix-length / funneling columns. |

### Designing an XLSX template from this dictionary

- **One row per `concept_key`.** Each row of `concept_aliases.yaml` is one entry in the XLSX. The `concept_key` (e.g. `biometry.bpd.measurement_mm`) is a stable identifier across template versions; the human-readable description goes in the next column over.
- **Seed columns from the concepts that already pair.** The 22 concepts in the table above are the safest seed because both source systems already capture them. An XLSX collecting them will accept data from both CUIMC-style and EVMS-style centers without ETL-side guesswork.
- **Add a `source coverage` column** marking each row as `both`, `observer-only`, or `viewpoint-only`. This tells the receiving center which fields their existing system already produces vs which need manual entry.
- **Drive cell format from the type column** (number, percentile, coded, free text, weeks+days). Numeric cells should be unformatted; percentile cells should accept `45%` or `0.45`; free-text cells should be wide-column.
- **The XLSX is upstream of the ETL.** Once it exists, a PhenoXtract-style YAML config wraps it back into Phenopackets via the same data dictionary you're reading now.

## Regenerate

```bash
uv run python src/prenatalppkt/scripts/data_dict/extract_all.py
uv run python src/prenatalppkt/scripts/data_dict/render_readme.py
```

## More detail

- [schema.md](schema.md) - CSV column schema, value-class tokens, pairing methodology
- [clusters.md](clusters.md) - 17 per-cluster field tables
