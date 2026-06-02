# prenatalppkt data dictionary

Cross-source field inventory for the prenatalppkt ETL. Every leaf path in the CUIMC Observer JSON corpus and every OBX-3 identifier in the EVMS GE HL7 v2.4 corpus appears here, grouped into clinical clusters, with Observer rows split per measurement label and Observer + HL7 fields paired on the same row whenever a label token and value class match.

`docs/data_dictionary/comparison.csv` is the canonical artifact (1512 rows: 1170 carry an Observer field, 374 carry an HL7 field, 32 pair both on one row). This README is generated from it; edit `render_readme.py`, `extract_all.py`, or `clusters.yaml`, never this file.

## For clinicians: cross-source field map

This section is a plain-language map of the data this pipeline ingests, written for clinicians. The technical schema starts at `## Regenerate` below; you can stop reading after this section if you only need the field-level vocabulary.

### What the two sources are

**Observer JSON** (CUIMC). A structured per-exam record exported by Columbia's prenatal-imaging system. Organized by fetus, with measurements, anatomy findings, and impressions stored as nested fields inside a single JSON file per exam. Strong on free-text narrative and multi-fetus structure; weaker on standardized HL7 codes.

**ViewPoint HL7** (EVMS, via GE). An HL7 v2.4 message stream exported from EVMS's GE ViewPoint system. Each finding is one OBX line with a system-specific field identifier (e.g. `SkullFetus.BiparietalDiameter`), a short label (e.g. `BPD`), and a value. Strong on standardized field naming; weaker on multi-fetus disambiguation and on free-text narrative.

The data dictionary below is built by walking both sources exhaustively and matching fields that hold the same clinical concept. `concept_aliases.yaml` lists the hand-curated matches; the current alias file declares 22 concepts.

### Concepts both systems capture (or only one side does)

The 22 concepts in `concept_aliases.yaml`, sorted by clinical area. `(Observer-only)` and `(ViewPoint-only)` mark concepts where only one source has the field; these are the ones the XLSX template will need to either collect by hand or infer at ETL time.

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

## Schema

Each CSV row is one Observer leaf (optionally with a single inherited measurement label), one HL7 OBX-3 identifier, or both when pairing fires. The 16 columns:

`concept_key` (clinical concept this row maps to, populated from `concept_aliases.yaml`; empty when no concept matches), `cluster`, `observer_path`, `observer_label_values`, `observer_type`, `observer_value_class`, `observer_sample`, `observer_n_files`, `viewpoint_path`, `viewpoint_short_label`, `viewpoint_long_label`, `viewpoint_type`, `viewpoint_value_class`, `viewpoint_sample`, `viewpoint_n_files`, `notes`.

## Value-class tokens

`empty`, `boolean`, `integer`, `decimal`, `percentile` (e.g. `56%`, `<5%`), `weeks_days` (e.g. `20w 3d`), `date`, `time`, `timestamp`, `coded_text` (short clinical enumeration), `free_text` (long-form narrative). HL7 viewpoint cells render sample values as `primary (display)` when the second OBX-5 caret-segment carries unit context (e.g. `163 (23w 2d)`, `45 (45%)`, `-0.9 (-0.9SD)`).

## Pairing

Pairing happens within each cluster, greedy first-fit. For each Observer record (one `(path, inherited-label)` tuple) the matcher builds a token set from the path leaf + the inherited measurement label; for each HL7 identifier it builds a token set from the identifier leaf + the OBX-3 short label + the OBX-3 long label. Tokens are matched case-insensitive after CamelCase / punctuation normalization. A pair fires when (a) at least one token overlaps and (b) value classes are compatible (direct overlap, or both sides are in the numeric family `{integer, decimal, percentile}`).

The label-split walker is what unlocks biometric pairings: `fetuses[].measurements[].value` is emitted as one record per inherited label (BPD / AC / HC / Femur / ...), so each measurement label can pair with its corresponding HL7 identifier instead of being collapsed into a single multi-label record that matched nothing.

### Paired rows by cluster

_Total: 32 paired cross-source rows._

| cluster | paired |
| --- | --- |
| biometry | 12 |
| cardiac | 12 |
| fetus_core | 1 |
| indication_impression | 2 |
| maternal_subject | 4 |
| non_fetal_gyn | 1 |

### Biometry pairings

Per-measurement Observer leaves paired with their HL7 namespace counterparts. Each row is one entry in the `biometry` cluster table below.

| observer leaf | label | HL7 identifier |
| --- | --- | --- |
| `calculated_ega` | AC | `AbdomenFetus.AbdominalCircumference` |
| `calculated_ega` | BPD | `SkullFetus.BiparietalDiameter` |
| `calculated_ega` | CRL | `EmbryonicStructuresFetus.CrownRumpLength` |
| `calculated_ega` | Femur | `ExtremitiesFetus.FemurUndefinedLength` |
| `calculated_ega` | HC | `SkullFetus.HeadCircumference` |
| `calculated_ega` | Humerus | `ExtremitiesFetus.HumerusUndefinedLength` |
| `calculated_ega` | Nuchal Fold | `NeckSkinFetus.NuchalFoldThickness` |
| `label` | AC | `U_FGRData_F_6v65c63705.AbdominalCircumference` |
| `label` | Nuchal Fold | `NeckSkinFetus.FetalAnatomyNuchalFoldAppearance` |
| `calculated_percentile` | FL/AC | `Fetus.FemurUndefinedLengthOverAbdominalCircumference` |
| `calculated_percentile` | FL/BPD | `Fetus.FemurUndefinedLengthOverBiparietalDiameter` |
| `calculated_percentile` | HC/AC | `Fetus.HeadCircumferenceOverAbdominalCircumference` |

### Clusters with zero paired rows

Several clusters carry only Observer or only HL7 records: Observer-only `anatomy_general` / `fetal_procedures` cover JSON wrapper shapes (no HL7 namespace exists for them); HL7-only `anatomy_brain` / `anatomy_face_neck` / `anatomy_chest_gi` / `anatomy_spine` / `anatomy_urinary` cover HL7 namespaces whose Observer counterparts live under free-text `anomalies` fields rather than as structured leaves. Clusters with both sides populated but zero pairs (e.g. `placenta_cord`, `amniotic_fluid`, `dating`, `encounter`) tokenize differently on the two sides; tightening those would need a hand-curated alias map.

## Clusters

### biometry

Fetal biometric measurements (HC, BPD, AC, FL, etc.), growth ratios, EFW values, first-trimester measurements (CRL, NT), and the GE FGR data block. Observer rows split by measurement label so each (BPD, AC, HC, ...) gets its own row.

_249 rows: 149 Observer, 112 HL7, 12 paired._

<!-- BEGIN: generated cluster=biometry -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | fetuses[].efws |  | empty |  |  |  |  |  |  |
|  | fetuses[].efws[].calculated_percentile | EFW (AC, BPD) | decimal\|integer | 51.2\|52\|81.1\|71.2 |  |  |  |  |  |
|  | fetuses[].efws[].calculated_percentile | EFW (AC, FL) | decimal | 63.7\|55.6\|61.8\|74.9 |  |  |  |  |  |
|  | fetuses[].efws[].calculated_percentile | EFW (AC, FL, HC) | decimal | 55.6\|36.3\|53.2\|65.2 |  |  |  |  |  |
|  | fetuses[].efws[].decimal_paces | EFW (AC, BPD) | integer | 0 |  |  |  |  |  |
|  | fetuses[].efws[].decimal_paces | EFW (AC, FL) | integer | 0 |  |  |  |  |  |
|  | fetuses[].efws[].decimal_paces | EFW (AC, FL, HC) | integer | 0 |  |  |  |  |  |
|  | fetuses[].efws[].fetus_number | EFW (AC, BPD) | integer | 1 |  |  |  |  |  |
|  | fetuses[].efws[].fetus_number | EFW (AC, FL) | integer | 1 |  |  |  |  |  |
|  | fetuses[].efws[].fetus_number | EFW (AC, FL, HC) | integer | 1 |  |  |  |  |  |
|  | fetuses[].efws[].label | EFW (AC, BPD) | coded_text | EFW (AC, BPD) |  |  |  |  |  |
|  | fetuses[].efws[].label | EFW (AC, FL) | coded_text | EFW (AC, FL) |  |  |  |  |  |
|  | fetuses[].efws[].label | EFW (AC, FL, HC) | coded_text | EFW (AC, FL, HC) |  |  |  |  |  |
|  | fetuses[].efws[].percentile_for_display | EFW (AC, BPD) | percentile | 51%\|52%\|81%\|71% |  |  |  |  |  |
|  | fetuses[].efws[].percentile_for_display | EFW (AC, FL) | percentile | 64%\|56%\|62%\|75% |  |  |  |  |  |
|  | fetuses[].efws[].percentile_for_display | EFW (AC, FL, HC) | percentile | 56%\|36%\|53%\|65% |  |  |  |  |  |
|  | fetuses[].efws[].print_in_report | EFW (AC, BPD) | integer | 0 |  |  |  |  |  |
|  | fetuses[].efws[].print_in_report | EFW (AC, FL) | integer | 0 |  |  |  |  |  |
|  | fetuses[].efws[].print_in_report | EFW (AC, FL, HC) | integer | 1 |  |  |  |  |  |
|  | fetuses[].efws[].range | EFW (AC, BPD) | empty |  |  |  |  |  |  |
|  | fetuses[].efws[].range | EFW (AC, FL) | empty |  |  |  |  |  |  |
|  | fetuses[].efws[].range | EFW (AC, FL, HC) | empty |  |  |  |  |  |  |
|  | fetuses[].efws[].value | EFW (AC, BPD) | decimal | 1000.887\|632.184\|3064.597\|1298.641 |  |  |  |  |  |
|  | fetuses[].efws[].value | EFW (AC, FL) | decimal | 1042.214\|638.934\|2858.504\|1316.907 |  |  |  |  |  |
|  | fetuses[].efws[].value | EFW (AC, FL, HC) | decimal | 1014.828\|598.194\|2778.253\|1273.729 |  |  |  |  |  |
|  | fetuses[].firsttrimester.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].firsttrimester.fet_pole_anom_txt |  | empty |  |  |  |  |  |  |
|  | fetuses[].firsttrimester.fetal_pole |  | coded_text | Unspecified\|Abnormal |  |  |  |  |  |
|  | fetuses[].firsttrimester.fetal_pole_anomalies |  | empty |  |  |  |  |  |  |
|  | fetuses[].firsttrimester.fetal_pole_size |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].firsttrimester.gest_sac_shape |  | coded_text | Unspecified\|Normal |  |  |  |  |  |
|  | fetuses[].firsttrimester.yolk_sac_pres |  | coded_text | Unspecified\|Seen |  |  |  |  |  |
|  | fetuses[].firsttrimester.yolk_sac_size_a |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].firsttrimester.yolk_sac_size_b |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].firsttrimester.yolk_sac_size_c |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].firsttrimester.yolk_sac_vol |  | integer | 0 |  |  |  |  |  |
| biometry.ac.measurement_mm | fetuses[].measurements[].calculated_ega | AC | decimal | 26.9\|23.7\|36.4\|29.7 | OBX AbdomenFetus.AbdominalCircumference | AC | decimal | 193.7\|145.5\|189.8\|281.3\|218.1\|179 (179.0) |  |
| biometry.bpd.measurement_mm | fetuses[].measurements[].calculated_ega | BPD | decimal | 26.9\|23.8\|37.9\|28.1 | OBX SkullFetus.BiparietalDiameter | BPD | decimal | 68.8\|39.4\|63.3\|78.5\|67.4\|53.4 |  |
| biometry.crl.measurement_mm | fetuses[].measurements[].calculated_ega | CRL | decimal | 11.3 | OBX EmbryonicStructuresFetus.CrownRumpLength | CRL | decimal | 70.7 |  |
|  | fetuses[].measurements[].calculated_ega | Cerebellum | decimal | 27.4 |  |  |  |  |  |
| biometry.femur.measurement_mm | fetuses[].measurements[].calculated_ega | Femur | decimal | 27.1\|23.6\|35.1\|27.4 | OBX ExtremitiesFetus.FemurUndefinedLength | Femur | decimal | 41.1\|25.4\|44.1\|63.2\|48.4\|39 (39.0) |  |
| biometry.hc.measurement_mm | fetuses[].measurements[].calculated_ega | HC | decimal\|integer | 26.9\|22.3\|35\|28.2 | OBX SkullFetus.HeadCircumference | HC | decimal | 225.2\|164.5\|234.7\|293.6\|240.9\|224.1 |  |
|  | fetuses[].measurements[].calculated_ega | Humerus | decimal | 23.8\|35.9 | OBX ExtremitiesFetus.HumerusUndefinedLength | Humerus | decimal | 22.5\|44.7 |  |
|  | fetuses[].measurements[].calculated_ega | Nuchal Fold | integer | 0 | OBX NeckSkinFetus.NuchalFoldThickness | Nuchal fold | decimal | 6.69 (6.7) |  |
| biometry.ac.percentile | fetuses[].measurements[].calculated_percentile | AC | decimal | 55.6\|50.4\|73.2\|87.5 |  |  |  |  |  |
| biometry.bpd.percentile | fetuses[].measurements[].calculated_percentile | BPD | decimal\|integer | 51.2\|53.2\|96\|42.1 |  |  |  |  |  |
| biometry.crl.percentile | fetuses[].measurements[].calculated_percentile | CRL | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_percentile | Cerebellum | integer | 0 |  |  |  |  |  |
| biometry.femur.percentile | fetuses[].measurements[].calculated_percentile | Femur | decimal | 46.8\|33.7\|39.4\|17.6 |  |  |  |  |  |
| biometry.hc.percentile | fetuses[].measurements[].calculated_percentile | HC | decimal | 42.5\|5.1\|15.9\|34.5 |  |  |  |  |  |
| biometry.humerus.percentile | fetuses[].measurements[].calculated_percentile | Humerus | decimal | 49.2\|64.1 |  |  |  |  |  |
| biometry.nuchal_fold.percentile | fetuses[].measurements[].calculated_percentile | Nuchal Fold | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_z_score | AC | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_z_score | BPD | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_z_score | CRL | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_z_score | Cerebellum | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_z_score | Femur | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_z_score | HC | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_z_score | Humerus | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].calculated_z_score | Nuchal Fold | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].decimal_places | AC | integer | 2 |  |  |  |  |  |
|  | fetuses[].measurements[].decimal_places | BPD | integer | 2 |  |  |  |  |  |
|  | fetuses[].measurements[].decimal_places | CRL | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].decimal_places | Cerebellum | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].decimal_places | Femur | integer | 2 |  |  |  |  |  |
|  | fetuses[].measurements[].decimal_places | HC | integer | 2 |  |  |  |  |  |
|  | fetuses[].measurements[].decimal_places | Humerus | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].decimal_places | Nuchal Fold | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].fetus_number | AC | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].fetus_number | BPD | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].fetus_number | CRL | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].fetus_number | Cerebellum | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].fetus_number | Femur | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].fetus_number | HC | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].fetus_number | Humerus | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].fetus_number | Nuchal Fold | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].include_in_avg_ga_calc | AC | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].include_in_avg_ga_calc | BPD | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].include_in_avg_ga_calc | CRL | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].include_in_avg_ga_calc | Cerebellum | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].include_in_avg_ga_calc | Femur | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].include_in_avg_ga_calc | HC | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].include_in_avg_ga_calc | Humerus | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].include_in_avg_ga_calc | Nuchal Fold | integer | 0 |  |  |  |  |  |
|  | fetuses[].measurements[].label | AC | coded_text | AC | OBX U_FGRData_F_6v65c63705.AbdominalCircumference | AC | coded_text | 193.7 mm \|145.5 mm , 145.5 mm , 145.5 mm , 145.5 mm \|189.8 mm , 189.8 mm , 189.8 mm \|281.3 mm , 281.3 mm , 281.3 mm \|218.1 mm , 218.1 mm , 218.1 mm \|179 mm , 179 mm , 179 mm , 179 mm  |  |
|  | fetuses[].measurements[].label | BPD | coded_text | BPD |  |  |  |  |  |
|  | fetuses[].measurements[].label | CRL | coded_text | CRL |  |  |  |  |  |
|  | fetuses[].measurements[].label | Cerebellum | coded_text | Cerebellum |  |  |  |  |  |
|  | fetuses[].measurements[].label | Femur | coded_text | Femur |  |  |  |  |  |
|  | fetuses[].measurements[].label | HC | coded_text | HC |  |  |  |  |  |
|  | fetuses[].measurements[].label | Humerus | coded_text | Humerus |  |  |  |  |  |
|  | fetuses[].measurements[].label | Nuchal Fold | coded_text | Nuchal Fold | OBX NeckSkinFetus.FetalAnatomyNuchalFoldAppearance | Nuchal fold | coded_text | abnormal |  |
|  | fetuses[].measurements[].percentile_for_display | AC | percentile | 56%\|50%\|73%\|88% |  |  |  |  |  |
|  | fetuses[].measurements[].percentile_for_display | BPD | percentile | 51%\|53%\|>95%\|42% |  |  |  |  |  |
|  | fetuses[].measurements[].percentile_for_display | CRL | empty |  |  |  |  |  |  |
|  | fetuses[].measurements[].percentile_for_display | Cerebellum | empty |  |  |  |  |  |  |
|  | fetuses[].measurements[].percentile_for_display | Femur | percentile | 47%\|34%\|39%\|18% |  |  |  |  |  |
|  | fetuses[].measurements[].percentile_for_display | HC | percentile | 43%\|5%\|16%\|35% |  |  |  |  |  |
|  | fetuses[].measurements[].percentile_for_display | Humerus | percentile | 49%\|64% |  |  |  |  |  |
|  | fetuses[].measurements[].percentile_for_display | Nuchal Fold | empty |  |  |  |  |  |  |
|  | fetuses[].measurements[].print_in_report | AC | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].print_in_report | BPD | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].print_in_report | CRL | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].print_in_report | Cerebellum | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].print_in_report | Femur | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].print_in_report | HC | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].print_in_report | Humerus | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].print_in_report | Nuchal Fold | integer | 1 |  |  |  |  |  |
|  | fetuses[].measurements[].unit_of_measure | AC | coded_text | cm |  |  |  |  |  |
|  | fetuses[].measurements[].unit_of_measure | BPD | coded_text | cm |  |  |  |  |  |
|  | fetuses[].measurements[].unit_of_measure | CRL | coded_text | mm |  |  |  |  |  |
|  | fetuses[].measurements[].unit_of_measure | Cerebellum | coded_text | cm |  |  |  |  |  |
|  | fetuses[].measurements[].unit_of_measure | Femur | coded_text | cm |  |  |  |  |  |
|  | fetuses[].measurements[].unit_of_measure | HC | coded_text | cm |  |  |  |  |  |
|  | fetuses[].measurements[].unit_of_measure | Humerus | coded_text | cm |  |  |  |  |  |
|  | fetuses[].measurements[].unit_of_measure | Nuchal Fold | coded_text | cm |  |  |  |  |  |
| biometry.ac.measurement_mm | fetuses[].measurements[].value | AC | decimal | 22.62\|19.12\|32.3\|25.5 |  |  |  |  |  |
| biometry.bpd.measurement_mm | fetuses[].measurements[].value | BPD | decimal\|integer | 6.68\|5.81\|9.31\|7 |  |  |  |  |  |
| biometry.crl.measurement_mm | fetuses[].measurements[].value | CRL | decimal | 4.48 |  |  |  |  |  |
|  | fetuses[].measurements[].value | Cerebellum | integer | 3 |  |  |  |  |  |
| biometry.femur.measurement_mm | fetuses[].measurements[].value | Femur | decimal | 5.01\|4.14\|6.92\|5.1 |  |  |  |  |  |
| biometry.hc.measurement_mm | fetuses[].measurements[].value | HC | decimal\|integer | 25\|20.31\|31.62\|26.2 |  |  |  |  |  |
| biometry.humerus.measurement_mm | fetuses[].measurements[].value | Humerus | decimal | 3.9\|6.2 |  |  |  |  |  |
| biometry.nuchal_fold.measurement_mm | fetuses[].measurements[].value | Nuchal Fold | integer | 1 |  |  |  |  |  |
|  | fetuses[].ratios |  | empty |  |  |  |  |  |  |
|  | fetuses[].ratios[].calculated_percentile | FL/AC | integer | 0 | OBX Fetus.FemurUndefinedLengthOverAbdominalCircumference | FL / AC | decimal | 0.2122 (0.21)\|0.1746 (0.17)\|0.2323 (0.23)\|0.2247 (0.22)\|0.2219 (0.22)\|0.2179 (0.22) |  |
|  | fetuses[].ratios[].calculated_percentile | FL/BPD | integer | 0 | OBX Fetus.FemurUndefinedLengthOverBiparietalDiameter | FL / BPD | decimal | 0.5974 (0.60)\|0.6447 (0.64)\|0.6967 (0.70)\|0.8051 (0.81)\|0.7181 (0.72)\|0.7303 (0.73) |  |
|  | fetuses[].ratios[].calculated_percentile | HC/AC | integer | 0 | OBX Fetus.HeadCircumferenceOverAbdominalCircumference | HC / AC | decimal | 1.16\|1.13\|1.24\|1.04\|1.1 (1.10)\|1.25 |  |
|  | fetuses[].ratios[].decimal_paces | FL/AC | integer | 0 |  |  |  |  |  |
|  | fetuses[].ratios[].decimal_paces | FL/BPD | integer | 0 |  |  |  |  |  |
|  | fetuses[].ratios[].decimal_paces | HC/AC | integer | 2 |  |  |  |  |  |
|  | fetuses[].ratios[].fetus_number | FL/AC | integer | 1 |  |  |  |  |  |
|  | fetuses[].ratios[].fetus_number | FL/BPD | integer | 1 |  |  |  |  |  |
|  | fetuses[].ratios[].fetus_number | HC/AC | integer | 1 |  |  |  |  |  |
|  | fetuses[].ratios[].label | FL/AC | coded_text | FL/AC |  |  |  |  |  |
|  | fetuses[].ratios[].label | FL/BPD | coded_text | FL/BPD |  |  |  |  |  |
|  | fetuses[].ratios[].label | HC/AC | coded_text | HC/AC |  |  |  |  |  |
|  | fetuses[].ratios[].percentile_for_display | FL/AC | empty |  |  |  |  |  |  |
|  | fetuses[].ratios[].percentile_for_display | FL/BPD | empty |  |  |  |  |  |  |
|  | fetuses[].ratios[].percentile_for_display | HC/AC | empty |  |  |  |  |  |  |
|  | fetuses[].ratios[].print_in_report | FL/AC | integer | 1 |  |  |  |  |  |
|  | fetuses[].ratios[].print_in_report | FL/BPD | integer | 1 |  |  |  |  |  |
|  | fetuses[].ratios[].print_in_report | HC/AC | integer | 1 |  |  |  |  |  |
|  | fetuses[].ratios[].range | FL/AC | coded_text | 20 - 24 |  |  |  |  |  |
|  | fetuses[].ratios[].range | FL/BPD | coded_text | 71 - 87 |  |  |  |  |  |
|  | fetuses[].ratios[].range | HC/AC | coded_text | 1.04 - 1.22\|1.05 - 1.21\|0.93 - 1.11\|1.05 - 1.22 |  |  |  |  |  |
|  | fetuses[].ratios[].value | FL/AC | decimal\|integer | 22.149\|21.653\|21.424\|20 |  |  |  |  |  |
|  | fetuses[].ratios[].value | FL/BPD | decimal\|integer | 75\|71.256\|74.329\|72.857 |  |  |  |  |  |
|  | fetuses[].ratios[].value | HC/AC | decimal | 1.105\|1.062\|0.979\|1.027 |  |  |  |  |  |
|  |  |  |  |  | OBX AbdomenFetus.AbdominalWallAppearance | Abdom. wall | coded_text | normal |  |
|  |  |  |  |  | OBX AbdomenFetus.InferiorVenaCavaDiameterZscoreMethod | IVC Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX AbdomenFetus.VP_AbdominalCircumference_Author |  | coded_text | Hadlock |  |
|  |  |  |  |  | OBX AbdomenFetus.VP_AbdominalCircumference_DevRatio |  | decimal\|percentile | -1.1 (-1.1%)\|5 (+5.0%)\|-3.1 (-3.1%)\|-1 (-1.0%)\|-9.5 (-9.5%)\|-7.1 (-7.1%) |  |
|  |  |  |  |  | OBX AbdomenFetus.VP_AbdominalCircumference_Deviation |  | decimal | -0.2 (-0.2SD)\|0.5 (+0.5SD)\|-0.5 (-0.5SD)\|-1.7 (-1.7SD)\|-1 (-1.0SD) |  |
|  |  |  |  |  | OBX AbdomenFetus.VP_AbdominalCircumference_GA |  | weeks_days | 169 (24w 1d)\|139 (19w 6d)\|166 (23w 5d)\|225 (32w 1d)\|184 (26w 2d)\|159 (22w 5d) |  |
|  |  |  |  |  | OBX AbdomenFetus.VP_AbdominalCircumference_Percentile |  | percentile | 43 (43%)\|70 (70%)\|32 (32%)\|42 (42%)\|4 (4%)\|15 (15%) |  |
|  |  |  |  |  | OBX EmbryonicStructuresFetus.VP_CrownRumpLength_Author |  | coded_text | Hadlock |  |
|  |  |  |  |  | OBX EmbryonicStructuresFetus.VP_CrownRumpLength_DevRatio |  | percentile | -1.4 (-1.4%) |  |
|  |  |  |  |  | OBX EmbryonicStructuresFetus.VP_CrownRumpLength_Deviation |  | decimal | -0.1 (-0.1SD) |  |
|  |  |  |  |  | OBX EmbryonicStructuresFetus.VP_CrownRumpLength_GA |  | weeks_days | 93 (13w 2d) |  |
|  |  |  |  |  | OBX EmbryonicStructuresFetus.VP_CrownRumpLength_Percentile |  | percentile | 45 (45%) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.FibulaUndefinedLength | Fibula | decimal | 17.3 |  |
|  |  |  |  |  | OBX ExtremitiesFetus.LowerExtremitiesAppearance | Legs | coded_text | suboptimal\|normal |  |
|  |  |  |  |  | OBX ExtremitiesFetus.TibiaUndefinedLength | Tibia | decimal | 17.3 |  |
|  |  |  |  |  | OBX ExtremitiesFetus.UpperExtremitiesAppearance | Arms | coded_text | suboptimal\|normal |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FemurUndefinedLength_Author |  | coded_text | Hadlock |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FemurUndefinedLength_DevRatio |  | decimal\|percentile | -6.2 (-6.2%)\|-15.8 (-15.8%)\|0.7 (+0.7%)\|-0.7 (-0.7%)\|-10.6 (-10.6%)\|-9.4 (-9.4%) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FemurUndefinedLength_Deviation |  | decimal | -0.9 (-0.9SD)\|-1.6 (-1.6SD)\|0.1 (+0.1SD)\|-0.1 (-0.1SD)\|-1.9 (-1.9SD)\|-1.3 (-1.3SD) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FemurUndefinedLength_GA |  | weeks_days | 163 (23w 2d)\|124 (17w 5d)\|172 (24w 4d)\|229 (32w 5d)\|184 (26w 2d)\|158 (22w 4d) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FemurUndefinedLength_Percentile |  | percentile | 18 (18%)\|6 (6%)\|54 (54%)\|44 (44%)\|3 (3%)\|9 (9%) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FibulaUndefinedLength_Author |  | coded_text | Romero |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FibulaUndefinedLength_DevRatio |  | percentile | -34.2 (-34.2%) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FibulaUndefinedLength_Deviation |  | decimal | -2.1 (-2.1SD) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_FibulaUndefinedLength_Percentile |  | percentile | 2 (2%) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_HumerusUndefinedLength_Author |  | coded_text | Romero |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_HumerusUndefinedLength_DevRatio |  | percentile | -20.5 (-20.5%)\|-7.4 (-7.4%) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_HumerusUndefinedLength_Deviation |  | decimal | -1.9 (-1.9SD)\|-1.2 (-1.2SD) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_HumerusUndefinedLength_Percentile |  | percentile | 3 (3%)\|12 (12%) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_TibiaUndefinedLength_Author |  | coded_text | Romero |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_TibiaUndefinedLength_DevRatio |  | percentile | -31.6 (-31.6%) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_TibiaUndefinedLength_Deviation |  | decimal | -2.6 (-2.6SD) |  |
|  |  |  |  |  | OBX ExtremitiesFetus.VP_TibiaUndefinedLength_Percentile |  | percentile | 0 (<1%) |  |
|  |  |  |  |  | OBX Fetus.BonyThoracicCircumferenceOverAbdominalCircumference | ThC / AC | decimal | 0.73221477 (0.73)\|0.89056902 (0.89) |  |
|  |  |  |  |  | OBX Fetus.EstimatedFetalWeight | EFW | decimal | 651.85456908 (652)\|260.66063565 (261)\|679.35773729 (679)\|1942.49329768 (1942)\|918.09260653 (918)\|536.32107116 (536) |  |
|  |  |  |  |  | OBX Fetus.EstimatedFetalWeightLb | EFW (lb) | integer | 1\|0\|4\|2 |  |
|  |  |  |  |  | OBX Fetus.EstimatedFetalWeightMethod | EFW by | coded_text | Hadlock (BPD-HC-AC-FL) |  |
|  |  |  |  |  | OBX Fetus.EstimatedFetalWeightOz | EFW (oz) | integer | 7\|9\|8\|5\|0\|3 |  |
|  |  |  |  |  | OBX Fetus.FemurUndefinedLengthOverHeadCircumference | FL / HC | decimal | 0.18\|0.15\|0.19\|0.22\|0.2 (0.20)\|0.17 |  |
|  |  |  |  |  | OBX Fetus.VP_EstimatedFetalWeight_DevRatio |  | decimal\|percentile | -2.7 (-2.7%)\|-7.3 (-7.3%)\|1.4 (+1.4%)\|-4.9 (-4.9%)\|-25.6 (-25.6%)\|-16.3 (-16.3%) |  |
|  |  |  |  |  | OBX Fetus.VP_EstimatedFetalWeight_Deviation |  | decimal | -0.2 (-0.2SD)\|-0.6 (-0.6SD)\|0.1 (+0.1SD)\|-0.4 (-0.4SD)\|-1.9 (-1.9SD)\|-1.2 (-1.2SD) |  |
|  |  |  |  |  | OBX Fetus.VP_EstimatedFetalWeight_Percentile |  | percentile | 42 (42%)\|29 (29%)\|54 (54%)\|36 (36%)\|3 (3%)\|11 (11%) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverAbdominalCircumference_Author |  | coded_text | Hadlock |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverAbdominalCircumference_DevRatio |  | percentile | -18.1 (-18.1%) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverAbdominalCircumference_Deviation |  | decimal | -3 (-3.0SD) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverAbdominalCircumference_Percentile |  | percentile | 0 (<1%) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverBiparietalDiameter_Author |  | coded_text | Hadlock |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverBiparietalDiameter_DevRatio |  | percentile | -5.2 (-5.2%) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverBiparietalDiameter_Deviation |  | decimal | -0.9 (-0.9SD) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverBiparietalDiameter_Percentile |  | percentile | 19 (19%) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverHeadCircumference_Author |  | coded_text | Hadlock |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverHeadCircumference_DevRatio |  | percentile | -17.3 (-17.3%) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverHeadCircumference_Deviation |  | decimal | -3.2 (-3.2SD) |  |
|  |  |  |  |  | OBX Fetus.VP_FemurUndefinedLengthOverHeadCircumference_Percentile |  | percentile | 0 (<1%) |  |
|  |  |  |  |  | OBX Fetus.VP_HeadCircumferenceOverAbdominalCircumference_Author |  | coded_text | Nicolaides |  |
|  |  |  |  |  | OBX Fetus.VP_HeadCircumferenceOverAbdominalCircumference_DevRatio |  | decimal\|percentile | 2 (+2.0%)\|-4.5 (-4.5%)\|9 (+9.0%)\|-1.6 (-1.6%)\|0.2 (+0.2%)\|9.6 (+9.6%) |  |
|  |  |  |  |  | OBX Fetus.VP_HeadCircumferenceOverAbdominalCircumference_Deviation |  | decimal | 0.4 (+0.4SD)\|-0.8 (-0.8SD)\|1.6 (+1.6SD)\|-0.3 (-0.3SD)\|0 (0.0SD)\|1.7 (+1.7SD) |  |
|  |  |  |  |  | OBX Fetus.VP_HeadCircumferenceOverAbdominalCircumference_Percentile |  | percentile | 64 (64%)\|20 (20%)\|95 (95%)\|40 (40%)\|51 (51%)\|96 (96%) |  |
|  |  |  |  |  | OBX NeckSkinFetus.NeckAppearance | Neck | coded_text | abnormal\|normal |  |
|  |  |  |  |  | OBX NeckSkinFetus.NeckDetails | Neck | coded_text | cystic hygroma |  |
|  |  |  |  |  | OBX NeckSkinFetus.NuchalTranslucency | NT | decimal | 4 (4.00) |  |
|  |  |  |  |  | OBX NeckSkinFetus.VP_NuchalTranslucency_Author |  | coded_text | Nicolaides |  |
|  |  |  |  |  | OBX NeckSkinFetus.VP_NuchalTranslucency_DevRatio |  | decimal | 110.2 (>+99%) |  |
|  |  |  |  |  | OBX NeckSkinFetus.VP_NuchalTranslucency_Deviation |  | decimal | 4.5 (+4.5SD) |  |
|  |  |  |  |  | OBX NeckSkinFetus.VP_NuchalTranslucency_Percentile |  | percentile | 100 (>99%) |  |
|  |  |  |  |  | OBX SkullFetus.BiparietalDiameterOverOccipitoFrontalDiameter | Cephalic index | decimal | 0.9596 (0.96)\|0.7519 (0.75)\|0.8474 (0.85)\|0.8396 (0.84)\|0.8787 (0.88)\|0.7489 (0.75) |  |
|  |  |  |  |  | OBX SkullFetus.HeadAppearance | Cranium | coded_text | abnormal\|normal |  |
|  |  |  |  |  | OBX SkullFetus.HeadDetails | Cranium | coded_text | cloverleaf shape |  |
|  |  |  |  |  | OBX SkullFetus.HeadShapeAppearance | Head shape | coded_text | abnormal |  |
|  |  |  |  |  | OBX SkullFetus.HeadShapeDetails | Head shape | coded_text | brachycephaly |  |
|  |  |  |  |  | OBX SkullFetus.HeadSizeAppearance | Head size | coded_text | normal |  |
|  |  |  |  |  | OBX SkullFetus.OccipitoFrontalDiameter | OFD | decimal | 71.7\|52.4\|74.7\|93.5\|76.7\|71.3 |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameterOverOccipitoFrontalDiameter_Author |  | coded_text | Nicolaides |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameterOverOccipitoFrontalDiameter_DevRatio |  | decimal\|percentile | 22.2 (+22.2%)\|-4.8 (-4.8%)\|7.9 (+7.9%)\|5.1 (+5.1%)\|11.5 (+11.5%)\|-4.6 (-4.6%) |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameterOverOccipitoFrontalDiameter_Deviation |  | decimal | 4.5 (+4.5SD)\|-1.1 (-1.1SD)\|1.7 (+1.7SD)\|1.1 (+1.1SD)\|2.4 (+2.4SD) |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameterOverOccipitoFrontalDiameter_Percentile |  | percentile | 100 (>99%)\|14 (14%)\|96 (96%)\|87 (87%)\|99 (>99%) |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameter_Author |  | coded_text | Hadlock |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameter_DevRatio |  | decimal\|percentile | 16.3 (+16.3%)\|-9.2 (-9.2%)\|7 (+7.0%)\|-3.5 (-3.5%)\|-5.1 (-5.1%)\|-8.4 (-8.4%) |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameter_Deviation |  | decimal | 3.2 (+3.2SD)\|-1.3 (-1.3SD)\|1.4 (+1.4SD)\|-1 (-1.0SD)\|-1.2 (-1.2SD)\|-1.6 (-1.6SD) |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameter_GA |  | weeks_days | 194 (27w 5d)\|126 (18w 0d)\|179 (25w 4d)\|221 (31w 4d)\|190 (27w 1d)\|156 (22w 2d) |  |
|  |  |  |  |  | OBX SkullFetus.VP_BiparietalDiameter_Percentile |  | percentile | 100 (>99%)\|9 (9%)\|92 (92%)\|17 (17%)\|12 (12%)\|5 (5%) |  |
|  |  |  |  |  | OBX SkullFetus.VP_HeadCircumference_Author |  | coded_text | Chervenak |  |
|  |  |  |  |  | OBX SkullFetus.VP_HeadCircumference_DevRatio |  | decimal\|percentile | 1.9 (+1.9%)\|6.2 (+6.2%)\|-2.3 (-2.3%)\|-8.5 (-8.5%)\|2.9 (+2.9%) |  |
|  |  |  |  |  | OBX SkullFetus.VP_HeadCircumference_Deviation |  | decimal | 0.3 (+0.3SD)\|0.9 (+0.9SD)\|-0.5 (-0.5SD)\|-1.5 (-1.5SD)\|0.4 (+0.4SD) |  |
|  |  |  |  |  | OBX SkullFetus.VP_HeadCircumference_GA |  | weeks_days | 171 (24w 3d)\|177 (25w 2d)\|221 (31w 4d)\|181 (25w 6d)\|170 (24w 2d) |  |
|  |  |  |  |  | OBX SkullFetus.VP_HeadCircumference_Percentile |  | percentile | 61 (61%)\|83 (83%)\|32 (32%)\|6 (6%)\|67 (67%) |  |
|  |  |  |  |  | OBX SkullFetus.VP_OccipitoFrontalDiameter_Author |  | coded_text | Nicolaides |  |
|  |  |  |  |  | OBX SkullFetus.VP_OccipitoFrontalDiameter_DevRatio |  | percentile | -7.1 (-7.1%)\|-7.6 (-7.6%)\|-3.3 (-3.3%)\|-12.7 (-12.7%)\|-18.1 (-18.1%)\|-6.2 (-6.2%) |  |
|  |  |  |  |  | OBX SkullFetus.VP_OccipitoFrontalDiameter_Deviation |  | decimal | -1.5 (-1.5SD)\|-1.6 (-1.6SD)\|-0.7 (-0.7SD)\|-2.8 (-2.8SD)\|-4.1 (-4.1SD)\|-1.3 (-1.3SD) |  |
|  |  |  |  |  | OBX SkullFetus.VP_OccipitoFrontalDiameter_GA |  | weeks_days | 155 (22w 1d)\|123 (17w 4d)\|160 (22w 6d)\|193 (27w 4d)\|164 (23w 3d) |  |
|  |  |  |  |  | OBX SkullFetus.VP_OccipitoFrontalDiameter_Percentile |  | percentile | 7 (7%)\|6 (6%)\|25 (25%)\|0 (<1%)\|10 (10%) |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.AbdominalCircumferencePercentile | 		AC %ile | percentile | 43% \|70% , 70% , 70% , 70% \|32% , 32% , 32% \|42% , 42% , 42% \|4% , 4% , 4% \|15% , 15% , 15% , 15%  |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.EFW | EFW | coded_text | 652 g \|261 g , 261 g , 261 g , 261 g \|679 g , 679 g , 679 g \|1942 g , 1942 g , 1942 g \|918 g , 918 g , 918 g \|536 g , 536 g , 536 g , 536 g  |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.EFWPercentile | 		EFW %ile | percentile | 42% \|29% , 29% , 29% , 29% \|54% , 54% , 54% \|36% , 36% , 36% \|3% , 3% , 3% \|11% , 11% , 11% , 11%  |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.UmbilicalArteryPI | UA PI | coded_text | ... \|... , ... , ... , ... \|... , ... , ... \|0.86 , 0.86 , 0.86  |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.UmbilicalArteryPIPercentile | 		UA PI %ile | percentile | ... \|... , ... , ... , ... \|... , ... , ... \|9% , 9% , 9%  |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.UmbilicalArteryRI | UA RI | coded_text | ... \|... , ... , ... , ... \|... , ... , ... \|0.54 , 0.54 , 0.54  |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.UmbilicalArteryRIPercentile | 		UA RI %ile | percentile | ... \|... , ... , ... , ... \|... , ... , ... \|4% , 4% , 4%  |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.UmbilicalArterySD | UA S/D | coded_text | ... \|... , ... , ... , ... \|... , ... , ... \|2.19 , 2.19 , 2.19  |  |
|  |  |  |  |  | OBX U_FGRData_F_6v65c63705.UmbilicalArterySDPercentile | 		UA SD %ile | percentile | ... \|... , ... , ... , ... \|... , ... , ... \|7% , 7% , 7%  |  |
<!-- END: generated cluster=biometry -->

### anatomy_brain

Fetal brain anatomy: ventricles, cerebellum, choroid plexus, posterior fossa.

_14 rows: 0 Observer, 14 HL7, 0 paired._

<!-- BEGIN: generated cluster=anatomy_brain -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | OBX BrainFetus.BrainAppearance | Brain | coded_text | abnormal\|normal |  |
|  |  |  |  |  | OBX BrainFetus.CerebellumAppearance | Cerebellum | coded_text | abnormal |  |
|  |  |  |  |  | OBX BrainFetus.CerebellumDetails | Cerebellum | coded_text | hypoplasia |  |
|  |  |  |  |  | OBX BrainFetus.LateralVentricleLAppearance | Lt lateral ventricle | coded_text | abnormal |  |
|  |  |  |  |  | OBX BrainFetus.LateralVentricleLDetails | Lt lateral ventricle | coded_text | ventriculomegaly |  |
|  |  |  |  |  | OBX BrainFetus.LateralVentricleRAppearance | Rt lateral ventricle | coded_text | abnormal |  |
|  |  |  |  |  | OBX BrainFetus.LateralVentricleRDetails | Rt lateral ventricle | coded_text | ventriculomegaly |  |
|  |  |  |  |  | OBX BrainFetus.LateralVentricleUndefinedOccipitalHorn | Vp | decimal | 13.78 (13.8)\|12.07 (12.1)\|0.73 (0.7) |  |
|  |  |  |  |  | OBX BrainFetus.TranscerebellarDiameter | Cerebellum tr | decimal | 19.3 |  |
|  |  |  |  |  | OBX BrainFetus.VP_TranscerebellarDiameter_Author |  | coded_text | Hill |  |
|  |  |  |  |  | OBX BrainFetus.VP_TranscerebellarDiameter_DevRatio |  | percentile | -3.5 (-3.5%) |  |
|  |  |  |  |  | OBX BrainFetus.VP_TranscerebellarDiameter_Deviation |  | decimal | -0.7 (-0.7SD) |  |
|  |  |  |  |  | OBX BrainFetus.VP_TranscerebellarDiameter_GA |  | weeks_days | 131 (18w 5d) |  |
|  |  |  |  |  | OBX BrainFetus.VP_TranscerebellarDiameter_Percentile |  | percentile | 26 (26%) |  |
<!-- END: generated cluster=anatomy_brain -->

### anatomy_face_neck

Fetal face and neck anatomy: orbits, lips, palate, profile, neck.

_3 rows: 0 Observer, 3 HL7, 0 paired._

<!-- BEGIN: generated cluster=anatomy_face_neck -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | OBX FaceFetus.FaceAppearance | Face | coded_text | suboptimal\|normal |  |
|  |  |  |  |  | OBX FaceFetus.InnerInterorbitalDistance | Inner IOD | decimal | 15 (15.0) |  |
|  |  |  |  |  | OBX FaceFetus.VP_InnerInterorbitalDistance_Author |  | coded_text | Merz |  |
<!-- END: generated cluster=anatomy_face_neck -->

### anatomy_chest_gi

Fetal chest (non-cardiac) and gastrointestinal anatomy.

_12 rows: 0 Observer, 12 HL7, 0 paired._

<!-- BEGIN: generated cluster=anatomy_chest_gi -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | OBX ChestFetus.BonyThoracicArea | Thoracic area | decimal | 1600.67 (16.0)\|2273.55 (22.7) |  |
|  |  |  |  |  | OBX ChestFetus.BonyThoracicCircumference | Thoracic circ | decimal | 141.83 (141.8)\|169.03 (169.0) |  |
|  |  |  |  |  | OBX ChestFetus.CardiacAreaOverBonyThoracicArea | CA / ThA | decimal | 0.28 |  |
|  |  |  |  |  | OBX ChestFetus.CardiacCircumferenceOverBonyThoracicCircumference | CC / ThC | decimal | 0.53 |  |
|  |  |  |  |  | OBX ChestFetus.ChestAppearance | Thorax | coded_text | normal |  |
|  |  |  |  |  | OBX ChestFetus.DuctusArteriosusDiameterZscoreMethod | Ductus arteriosus Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX ChestFetus.ThoracicDescAortaDetails | Descending aorta | coded_text | normal |  |
|  |  |  |  |  | OBX ChestFetus.VP_BonyThoracicCircumference_Author |  | coded_text | Lessoway |  |
|  |  |  |  |  | OBX ChestFetus.VP_BonyThoracicCircumference_DevRatio |  | percentile | -16.8 (-16.8%)\|-0.9 (-0.9%) |  |
|  |  |  |  |  | OBX ChestFetus.VP_BonyThoracicCircumference_Deviation |  | decimal | -2 (-2.0SD)\|-0.1 (-0.1SD) |  |
|  |  |  |  |  | OBX ChestFetus.VP_BonyThoracicCircumference_Percentile |  | percentile | 2 (2%)\|46 (46%) |  |
|  |  |  |  |  | OBX GastrointestinalTractFetus.GastrointestinalTractAppearance | GI tract | coded_text | normal |  |
<!-- END: generated cluster=anatomy_chest_gi -->

### anatomy_spine

Fetal spine anatomy.

_1 rows: 0 Observer, 1 HL7, 0 paired._

<!-- BEGIN: generated cluster=anatomy_spine -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | OBX SpineFetus.SpineAppearance | Spine | coded_text | suboptimal\|normal |  |
<!-- END: generated cluster=anatomy_spine -->

### anatomy_urinary

Fetal genitourinary anatomy: kidneys, bladder, ureters.

_46 rows: 0 Observer, 46 HL7, 0 paired._

<!-- BEGIN: generated cluster=anatomy_urinary -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | OBX UrinaryTractFetus.BladderAppearance | Bladder | coded_text | normal |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyLAnteriorPosteriorDiameter | Lt Kidney ap | decimal | 30.9 |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyLAppearance | Lt kidney | coded_text | abnormal |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyLLongitudinalDiameter | Lt Kidney long | decimal | 43.6 |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyLTransverseDiameter | Lt Kidney tr | decimal | 45.9 |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyLVolume | Lt Kidney Vol | decimal | 32378 (32.4) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyRAnteriorPosteriorDiameter | Rt Kidney ap | decimal | 25.7 |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyRAppearance | Rt kidney | coded_text | abnormal |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyRLongitudinalDiameter | Rt Kidney long | decimal | 45.2 |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyRTransverseDiameter | Rt Kidney tr | decimal | 27.5 |  |
|  |  |  |  |  | OBX UrinaryTractFetus.KidneyRVolume | Rt Kidney Vol | decimal | 16726 (16.7) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.RenalPelvisLAnteriorPosteriorDiameter | Lt Renal pelvis ap | decimal | 13.35 (13.4) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.RenalPelvisRAnteriorPosteriorDiameter | Rt Renal pelvis ap | decimal | 11.18 (11.2) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.UrogenitalTractAppearance | Urogenital tract | coded_text | normal\|abnormal |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLAnteriorPosteriorDiameter_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLAnteriorPosteriorDiameter_DevRatio |  | decimal | 32.5 (+32.5%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLAnteriorPosteriorDiameter_Deviation |  | decimal | 1.9 (+1.9SD) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLAnteriorPosteriorDiameter_Percentile |  | percentile | 97 (97%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLLongitudinalDiameter_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLLongitudinalDiameter_DevRatio |  | decimal | 12.5 (+12.5%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLLongitudinalDiameter_Deviation |  | decimal | 1 (+1.0SD) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLLongitudinalDiameter_Percentile |  | percentile | 83 (83%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLTransverseDiameter_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLTransverseDiameter_DevRatio |  | decimal | 102.6 (>+99%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLVolume_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLVolume_DevRatio |  | decimal | 201.8 (>+99%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLVolume_Deviation |  | decimal | 5.2 (+5.2SD) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyLVolume_Percentile |  | percentile | 100 (>99%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRAnteriorPosteriorDiameter_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRAnteriorPosteriorDiameter_DevRatio |  | decimal | 10.2 (+10.2%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRAnteriorPosteriorDiameter_Deviation |  | decimal | 0.6 (+0.6SD) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRAnteriorPosteriorDiameter_Percentile |  | percentile | 72 (72%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRLongitudinalDiameter_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRLongitudinalDiameter_DevRatio |  | decimal | 16.6 (+16.6%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRLongitudinalDiameter_Deviation |  | decimal | 1.3 (+1.3SD) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRLongitudinalDiameter_Percentile |  | percentile | 90 (90%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRTransverseDiameter_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRTransverseDiameter_DevRatio |  | decimal | 21.4 (+21.4%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRTransverseDiameter_Deviation |  | decimal | 1.2 (+1.2SD) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRTransverseDiameter_Percentile |  | percentile | 89 (89%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRVolume_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRVolume_DevRatio |  | decimal | 55.9 (+55.9%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRVolume_Deviation |  | decimal | 1.4 (+1.4SD) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_KidneyRVolume_Percentile |  | percentile | 92 (92%) |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_RenalPelvisLAnteriorPosteriorDiameter_Author |  | coded_text | Chitty |  |
|  |  |  |  |  | OBX UrinaryTractFetus.VP_RenalPelvisRAnteriorPosteriorDiameter_Author |  | coded_text | Chitty |  |
<!-- END: generated cluster=anatomy_urinary -->

### anatomy_general

System-agnostic anatomy wrapper fields (main / detail / anomalies metadata) that apply across organ systems.

_295 rows: 295 Observer, 0 HL7, 0 paired._

<!-- BEGIN: generated cluster=anatomy_general -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | fetuses[].anatomy[].anomalies |  | empty |  |  |  |  |  |  |
|  | fetuses[].anatomy[].anomalies[].abnormal_or_normal_variant |  | coded_text | Abnormal |  |  |  |  |  |
|  | fetuses[].anatomy[].anomalies[].description |  | coded_text | Dandy Walker\|Renal agenesis\|Omphalocele\|Acrania\|Hypoplastic left ventricle |  |  |  |  |  |
|  | fetuses[].anatomy[].detail |  | empty |  |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | BPD Level | coded_text | Unseen\|Normal |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Bowel | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Calvarium | coded_text | Unseen\|Normal\|Abnormal |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Cardiac Axis | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Cardiac Position | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Cerebellum | coded_text | Abnormal\|Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Cervical Spine | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Choroid Plexus | coded_text | Unseen\|Normal |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Cisterna Magna | coded_text | Unseen\|Normal |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Diaphragm | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Distal Left Outflow | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Distal Right Outflow | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Face | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Four Chamber View | coded_text | Normal\|Unseen\|Abnormal |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Gall Bladder | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | IVC | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Interatrial Septum | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Interventricular Septum | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lateral Ventricles | coded_text | Unseen\|Normal |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Liver | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lt Femur | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lt Fingers | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lt Foot | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lt Forearm | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lt Hand | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lt Humerus | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lt Low Leg | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lt Toes | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lumbar Spine | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Lungs | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Neck | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Nose/Lips | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Nuchal Fold | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Orbits | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Palate | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Profile | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Proximal Left Outflow | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Proximal Right Outflow | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Rt Femur | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Rt Fingers | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Rt Foot | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Rt Forearm | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Rt Hand | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Rt Humerus | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Rt Low Leg | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Rt Toes | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | SVC | coded_text | Unseen\|Normal |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Sacrum | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Short Axis of Greater Vessels | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Spleen | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].anat_det_state | Thoracic Spine | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | BPD Level | coded_text | BPD Level |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Bowel | coded_text | Bowel |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Calvarium | coded_text | Calvarium |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Cardiac Axis | coded_text | Cardiac Axis |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Cardiac Position | coded_text | Cardiac Position |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Cerebellum | coded_text | Cerebellum |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Cervical Spine | coded_text | Cervical Spine |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Choroid Plexus | coded_text | Choroid Plexus |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Cisterna Magna | coded_text | Cisterna Magna |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Diaphragm | coded_text | Diaphragm |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Distal Left Outflow | coded_text | Distal Left Outflow |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Distal Right Outflow | coded_text | Distal Right Outflow |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Face | coded_text | Face |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Four Chamber View | coded_text | Four Chamber View |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Gall Bladder | coded_text | Gall Bladder |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | IVC | coded_text | IVC |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Interatrial Septum | coded_text | Interatrial Septum |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Interventricular Septum | coded_text | Interventricular Septum |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lateral Ventricles | coded_text | Lateral Ventricles |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Liver | coded_text | Liver |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lt Femur | coded_text | Lt Femur |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lt Fingers | coded_text | Lt Fingers |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lt Foot | coded_text | Lt Foot |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lt Forearm | coded_text | Lt Forearm |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lt Hand | coded_text | Lt Hand |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lt Humerus | coded_text | Lt Humerus |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lt Low Leg | coded_text | Lt Low Leg |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lt Toes | coded_text | Lt Toes |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lumbar Spine | coded_text | Lumbar Spine |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Lungs | coded_text | Lungs |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Neck | coded_text | Neck |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Nose/Lips | coded_text | Nose/Lips |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Nuchal Fold | coded_text | Nuchal Fold |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Orbits | coded_text | Orbits |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Palate | coded_text | Palate |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Profile | coded_text | Profile |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Proximal Left Outflow | coded_text | Proximal Left Outflow |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Proximal Right Outflow | coded_text | Proximal Right Outflow |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Rt Femur | coded_text | Rt Femur |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Rt Fingers | coded_text | Rt Fingers |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Rt Foot | coded_text | Rt Foot |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Rt Forearm | coded_text | Rt Forearm |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Rt Hand | coded_text | Rt Hand |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Rt Humerus | coded_text | Rt Humerus |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Rt Low Leg | coded_text | Rt Low Leg |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Rt Toes | coded_text | Rt Toes |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | SVC | coded_text | SVC |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Sacrum | coded_text | Sacrum |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Short Axis of Greater Vessels | coded_text | Short Axis of Greater Vessels |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Spleen | coded_text | Spleen |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].label | Thoracic Spine | coded_text | Thoracic Spine |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | BPD Level | integer | 0\|1 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Bowel | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Calvarium | integer | 0\|1 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Cardiac Axis | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Cardiac Position | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Cerebellum | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Cervical Spine | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Choroid Plexus | integer | 0\|1 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Cisterna Magna | integer | 0\|1 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Diaphragm | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Distal Left Outflow | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Distal Right Outflow | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Face | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Four Chamber View | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Gall Bladder | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | IVC | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Interatrial Septum | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Interventricular Septum | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lateral Ventricles | integer | 0\|1 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Liver | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lt Femur | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lt Fingers | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lt Foot | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lt Forearm | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lt Hand | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lt Humerus | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lt Low Leg | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lt Toes | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lumbar Spine | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Lungs | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Neck | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Nose/Lips | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Nuchal Fold | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Orbits | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Palate | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Profile | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Proximal Left Outflow | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Proximal Right Outflow | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Rt Femur | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Rt Fingers | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Rt Foot | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Rt Forearm | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Rt Hand | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Rt Humerus | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Rt Low Leg | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Rt Toes | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | SVC | integer | 0\|1 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Sacrum | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Short Axis of Greater Vessels | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Spleen | integer | 0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].print_in_report | Thoracic Spine | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | BPD Level | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Bowel | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Calvarium | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Cardiac Axis | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Cardiac Position | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Cerebellum | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Cervical Spine | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Choroid Plexus | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Cisterna Magna | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Diaphragm | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Distal Left Outflow | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Distal Right Outflow | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Face | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Four Chamber View | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Gall Bladder | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | IVC | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Interatrial Septum | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Interventricular Septum | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lateral Ventricles | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Liver | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lt Femur | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lt Fingers | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lt Foot | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lt Forearm | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lt Hand | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lt Humerus | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lt Low Leg | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lt Toes | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lumbar Spine | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Lungs | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Neck | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Nose/Lips | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Nuchal Fold | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Orbits | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Palate | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Profile | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Proximal Left Outflow | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Proximal Right Outflow | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Rt Femur | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Rt Fingers | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Rt Foot | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Rt Forearm | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Rt Hand | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Rt Humerus | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Rt Low Leg | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Rt Toes | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | SVC | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Sacrum | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Short Axis of Greater Vessels | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Spleen | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required | Thoracic Spine | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required_condition_met | BPD Level | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required_condition_met | Calvarium | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required_condition_met | Cerebellum | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required_condition_met | Choroid Plexus | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required_condition_met | Cisterna Magna | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].detail[].required_condition_met | Lateral Ventricles | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Abd. Cav. | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Abd. Wall | coded_text | Normal\|Abnormal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Bladder | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Extrems | coded_text | Normal\|See details\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Face/Neck | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Genitalia | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Head | coded_text | Abnormal\|Normal |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Heart | coded_text | Normal\|See details\|Unseen\|Abnormal |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Left Kidney | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | PCI | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Placenta | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Right Kidney | coded_text | Normal\|Abnormal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Spine | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Stomach | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Th. Cav. | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.anat_state | Umbl. Cord | coded_text | Normal\|Unseen |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Abd. Cav. | coded_text | Abd. Cav. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Abd. Wall | coded_text | Abd. Wall |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Bladder | coded_text | Bladder |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Extrems | coded_text | Extrems |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Face/Neck | coded_text | Face/Neck |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Genitalia | coded_text | Genitalia |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Head | coded_text | Head |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Heart | coded_text | Heart |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Left Kidney | coded_text | Left Kidney |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | PCI | coded_text | PCI |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Placenta | coded_text | Placenta |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Right Kidney | coded_text | Right Kidney |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Spine | coded_text | Spine |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Stomach | coded_text | Stomach |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Th. Cav. | coded_text | Th. Cav. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.label | Umbl. Cord | coded_text | Umbl. Cord |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Abd. Cav. | coded_text | The abdominal cavity appears normal.\|The abdominal cavity was not assessed. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Abd. Wall | coded_text | The abdominal wall appears intact.\|Abnormal abdominal wall: please see the anatomy comments for further details.\|The abdominal wall was not visualized due to fetal position. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Bladder | coded_text | The fetal bladder appears normal.\|The fetal bladder was not assessed on today's exam. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Extrems | coded_text\|empty\|free_text | Active movement of the extremities was seen and fetal body motion was also observed during this examination.\|The fetal extremities were not assessed on today's exam. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Face/Neck | coded_text | The fetal face appears normal.\|The fetal face was not assessed on today's exam. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Genitalia | coded_text | Normal <gender> genitalia.\|The genitalia were not observed during this examination due to fetal position. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Head | free_text | Abnormalities in the head were noted during this scan; please see the anatomy comments.\|The fetal cranium appeared normal in shape. The choroid plexus was well visualized, the lateral ventricles were not dilated and the midline structures were not deviated. The cerebellum and cisterna magna were visualized and appeared normal. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Heart | coded_text\|empty\|free_text | The cardiac size and structures appeared sonographically normal at the four chamber view, and cardiac rhythm was regular.\|The fetal heart was not assessed on today's exam.\|Abnormal heart:  please see the anatomy comments for further details. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Left Kidney | coded_text\|free_text | The left kidney appears within normal limits with respect to size, collection systems, and parenchyma.\|The left kidney was not observed during this exam. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | PCI | empty |  |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Placenta | coded_text | The placenta appears within normal limits.\|The placenta was not evaluated on today's exam. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Right Kidney | coded_text\|free_text | The right kidney appears within normal limits with respect to size, collection systems, and parenchyma.\|Abnormalities were noted in the right kidney:  please see the anatomy comments for further details.\|The right kidney was not observed during this exam. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Spine | coded_text\|free_text | The spine was visualized from cervical to sacral region, within the resolution of the ultrasound equipment, without evidence of a neural tube defect.\|The fetal spine was not visualized on today's exam due to fetal position. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Stomach | coded_text | The fetal stomach appears normal.\|The fetal stomach was not assessed on today's exam. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Th. Cav. | coded_text | Anatomy of the fetal thorax appeared within normal limits.\|The thoracic cavity was not evaluated for this exam due to fetal position. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.main_txt | Umbl. Cord | coded_text | There is a 3 vessel cord with normal insertion site.\|The 3-vessel umbilical cord insertion was not visualized due to fetal position. |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Abd. Cav. | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Abd. Wall | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Bladder | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Extrems | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Face/Neck | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Genitalia | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Head | integer | 1 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Heart | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Left Kidney | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | PCI | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Placenta | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Right Kidney | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Spine | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Stomach | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Th. Cav. | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.print_in_report | Umbl. Cord | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Abd. Cav. | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Abd. Wall | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Bladder | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Extrems | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Face/Neck | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Genitalia | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Head | coded_text | Yes |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Heart | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Left Kidney | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | PCI | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Placenta | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Right Kidney | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Spine | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Stomach | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Th. Cav. | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required | Umbl. Cord | coded_text | No |  |  |  |  |  |
|  | fetuses[].anatomy[].main.required_condition_met | Head | coded_text | Yes |  |  |  |  |  |
<!-- END: generated cluster=anatomy_general -->

### cardiac

Fetal cardiac anatomy and echocardiography measurements; heart-specific findings on both sides.

_306 rows: 243 Observer, 75 HL7, 12 paired._

<!-- BEGIN: generated cluster=cardiac -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | fetuses[].dm_echo.aortic_root_diameter.biventricular_inner_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.biventricular_outer_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.comment.formatted_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.comment.plain_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.inner_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.inner_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.internal_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.internal_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.outer_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.outer_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.root_diameter |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.wall_thickness_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.aortic_root_diameter.wall_thickness_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.biventricular_inner_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.biventricular_outer_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.comment.formatted_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.comment.plain_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.inner_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.inner_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.internal_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.internal_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.outer_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.outer_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.root_diameter |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.wall_thickness_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.biventricular_dimensions.wall_thickness_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.biventricular_inner_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.biventricular_outer_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.comment.formatted_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.comment.plain_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.inner_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.inner_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.internal_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.internal_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.outer_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.outer_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.root_diameter |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.wall_thickness_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.interventricular_septum.wall_thickness_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.biventricular_inner_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.biventricular_outer_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.comment.formatted_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.comment.plain_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.inner_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.inner_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.internal_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.internal_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.outer_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.outer_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.root_diameter |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.wall_thickness_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricle.wall_thickness_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.biventricular_inner_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.biventricular_outer_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.comment.formatted_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.comment.plain_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.inner_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.inner_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.internal_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.internal_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.outer_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.outer_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.root_diameter |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.wall_thickness_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.left_ventricular.wall_thickness_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.biventricular_inner_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.biventricular_outer_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.comment.formatted_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.comment.plain_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.inner_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.inner_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.internal_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.internal_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.outer_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.outer_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.root_diameter |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.wall_thickness_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.pulmonary_root_diameter.wall_thickness_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.biventricular_inner_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.biventricular_outer_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.comment.formatted_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.comment.plain_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.inner_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.inner_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.internal_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.internal_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.outer_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.outer_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.root_diameter |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.wall_thickness_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricle.wall_thickness_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.biventricular_inner_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.biventricular_outer_fractional_shortening |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.comment.formatted_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.comment.plain_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.inner_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.inner_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.internal_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.internal_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.outer_dimension_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.outer_dimension_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.root_diameter |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.wall_thickness_diastole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].dm_echo.right_ventricular.wall_thickness_systole |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].anomalies |  | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].detail |  | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | 3 Vessel view | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | 3 Vessel-trachea view | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | 4 chamber view apical | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | 4 chamber view subcostal | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Aortic Arch | coded_text | Unseen | OBX FetalEchocardiography.AorticArchDetails | Aortic arch | coded_text | normal |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Aortic valve | coded_text | Unseen | OBX HeartFetus.AorticValveDetails | Aortic valve | coded_text | mild aortic regurgitation\|normal size and morphology |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Atrial septum | coded_text | Unseen | OBX HeartFetus.AtrialSeptumDetails | Atrial septum | coded_text | normal size and morphology\|aneurysmal flap valve, normal size and morphology |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Ductal Arch | coded_text | Unseen | OBX FetalEchocardiography.DuctusArteriosusDetails | Ductal arch | coded_text | normal\|forward unaliased flow, normal |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Ductus venosus | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Foramen ovale | coded_text | Unseen | OBX HeartFetus.ForamenOvaleDetails | Foramen ovale | coded_text | normal (in the central third/half, flap valve in left atrium) |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Inferior vena cava | coded_text | Unseen | OBX FetalEchocardiography.InferiorVenaCavaDetails | IVC | coded_text | normal |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | LVOT | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | M-mode/rhythm | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Mitral valve | coded_text | Unseen | OBX HeartFetus.MitralValveDetails | Mitral valve | coded_text | normal size and morphology |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Pulmonary valve | coded_text | Unseen | OBX HeartFetus.PulmonaryValveDetails | Pulmonary valve | coded_text | pulmonary stenosis\|normal size and morphology |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Pulmonary veins | coded_text | Unseen | OBX HeartFetus.PulmonaryVeinsDetails | Pulmonary veins | coded_text | normal |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | RVOT | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Short Axis ventricles | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Short axis outflows | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Superior vena cava | coded_text | Unseen | OBX FetalEchocardiography.SuperiorVenaCavaDetails | SVC | coded_text | normal |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Tricuspid valve | coded_text | Unseen | OBX HeartFetus.TricuspidValveDetails | Tricuspid valve | coded_text | dysplasia, normal size and morphology |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Umbilical artery | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Umbilical vein | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Ventricular septum | coded_text | Unseen | OBX HeartFetus.VentricularSeptumDetails | Ventricular septum | coded_text | intact |  |
|  | fetuses[].fetal_echo_anatomy[].main.anat_state | Visceral/abdominal situs | coded_text | Unseen |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | 3 Vessel view | coded_text | 3 Vessel view |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | 3 Vessel-trachea view | coded_text | 3 Vessel-trachea view |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | 4 chamber view apical | coded_text | 4 chamber view apical |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | 4 chamber view subcostal | coded_text | 4 chamber view subcostal |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Aortic Arch | coded_text | Aortic Arch |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Aortic valve | coded_text | Aortic valve |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Atrial septum | coded_text | Atrial septum |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Ductal Arch | coded_text | Ductal Arch |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Ductus venosus | coded_text | Ductus venosus |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Foramen ovale | coded_text | Foramen ovale |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Inferior vena cava | coded_text | Inferior vena cava |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | LVOT | coded_text | LVOT |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | M-mode/rhythm | coded_text | M-mode/rhythm |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Mitral valve | coded_text | Mitral valve |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Pulmonary valve | coded_text | Pulmonary valve |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Pulmonary veins | coded_text | Pulmonary veins |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | RVOT | coded_text | RVOT |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Short Axis ventricles | coded_text | Short Axis ventricles |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Short axis outflows | coded_text | Short axis outflows |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Superior vena cava | coded_text | Superior vena cava |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Tricuspid valve | coded_text | Tricuspid valve |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Umbilical artery | coded_text | Umbilical artery |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Umbilical vein | coded_text | Umbilical vein |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Ventricular septum | coded_text | Ventricular septum |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.label | Visceral/abdominal situs | coded_text | Visceral/abdominal situs |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | 3 Vessel view | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | 3 Vessel-trachea view | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | 4 chamber view apical | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | 4 chamber view subcostal | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Aortic Arch | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Aortic valve | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Atrial septum | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Ductal Arch | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Ductus venosus | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Foramen ovale | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Inferior vena cava | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | LVOT | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | M-mode/rhythm | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Mitral valve | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Pulmonary valve | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Pulmonary veins | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | RVOT | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Short Axis ventricles | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Short axis outflows | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Superior vena cava | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Tricuspid valve | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Umbilical artery | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Umbilical vein | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Ventricular septum | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.main_txt | Visceral/abdominal situs | empty |  |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | 3 Vessel view | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | 3 Vessel-trachea view | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | 4 chamber view apical | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | 4 chamber view subcostal | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Aortic Arch | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Aortic valve | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Atrial septum | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Ductal Arch | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Ductus venosus | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Foramen ovale | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Inferior vena cava | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | LVOT | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | M-mode/rhythm | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Mitral valve | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Pulmonary valve | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Pulmonary veins | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | RVOT | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Short Axis ventricles | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Short axis outflows | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Superior vena cava | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Tricuspid valve | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Umbilical artery | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Umbilical vein | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Ventricular septum | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.print_in_report | Visceral/abdominal situs | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | 3 Vessel view | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | 3 Vessel-trachea view | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | 4 chamber view apical | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | 4 chamber view subcostal | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Aortic Arch | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Aortic valve | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Atrial septum | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Ductal Arch | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Ductus venosus | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Foramen ovale | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Inferior vena cava | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | LVOT | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | M-mode/rhythm | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Mitral valve | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Pulmonary valve | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Pulmonary veins | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | RVOT | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Short Axis ventricles | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Short axis outflows | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Superior vena cava | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Tricuspid valve | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Umbilical artery | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Umbilical vein | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Ventricular septum | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_anatomy[].main.required | Visceral/abdominal situs | coded_text | No |  |  |  |  |  |
|  | fetuses[].fetal_echo_measurements |  | empty |  |  |  |  |  |  |
|  | fetuses[].fetus.heart_bpm |  | integer | 150\|161 |  |  |  |  |  |
|  | fetuses[].fetus.heart_movement_seen |  | coded_text | Seen |  |  |  |  |  |
|  | fetuses[].fetus.heart_rate_is |  | coded_text | Regular |  |  |  |  |  |
|  |  |  |  |  | OBX FetalEchocardiography.FetalEchoMarkersOtherFindingsPrint | Fetal echocardiography markers other findings print | coded_text | Print |  |
|  |  |  |  |  | OBX FetalEchocardiography.ThymusTTRatioPrint | Thymus print | coded_text | Print |  |
|  |  |  |  |  | OBX HeartFetus.AortaAscDetails | Ascending aorta | coded_text | normal size and morphology |  |
|  |  |  |  |  | OBX HeartFetus.AorticIsthmusDetails | Aortic isthmus | coded_text | normal size and morphology |  |
|  |  |  |  |  | OBX HeartFetus.AorticIsthmusDiameterZscoreMethod | Ao isthmus Zscore by | coded_text | Krishnan |  |
|  |  |  |  |  | OBX HeartFetus.AorticRootDetails | Aortic root | coded_text | aortic root larger than pulmonary root\|normal |  |
|  |  |  |  |  | OBX HeartFetus.AorticValveAnnulusDiameterSystole2D | AoV annulus syst | decimal | 6.3\|8.5 |  |
|  |  |  |  |  | OBX HeartFetus.AorticValveAnnulusDiameterSystole2DZscoreBPD | AoV annulus syst Z-score (BPD) | decimal | 2.92371661 (2.92)\|5.87769032 (5.88) |  |
|  |  |  |  |  | OBX HeartFetus.AorticValveAnnulusDiameterSystole2DZscoreFL | AoV annulus syst Z-score (FL) | decimal | 4.93056572 (4.93)\|7.07297098 (7.07) |  |
|  |  |  |  |  | OBX HeartFetus.AorticValveAnnulusDiameterSystole2DZscoreGA | AoV annulus syst Z-score (GA) | decimal | 4.23621336 (4.24)\|6.57253575 (6.57) |  |
|  |  |  |  |  | OBX HeartFetus.AorticValveAnnulusDiameterSystole2DZscoreMethod | AoV annulus syst Z-score by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.AorticValveDiameterOverPulmonaryValveDiameterSystole | AoV annulus syst / PV annulus syst | decimal | 0.91970803 (0.92)\|0.82284608 (0.82) |  |
|  |  |  |  |  | OBX HeartFetus.AscendingAortaDiameterZscoreMethod | Ao asc Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.AtriaDetails | Atria | coded_text | normal, atria approximately equal in size |  |
|  |  |  |  |  | OBX HeartFetus.AtrioVentricularConnectionsDetails | AV connections | coded_text | common AV junction, balanced ventricles\|concordant, patent AV valves, equal size |  |
|  |  |  |  |  | OBX HeartFetus.CardiacActivity | Cardiac activity | coded_text | present |  |
|  |  |  |  |  | OBX HeartFetus.CardiacArea | Cardiac area | decimal | 450.02 (4.5)\|647.73 (6.5) |  |
|  |  |  |  |  | OBX HeartFetus.CardiacCircumference | Cardiac circ | decimal | 75.2\|90.22 (90.2) |  |
|  |  |  |  |  | OBX HeartFetus.CardiacFunction | Cardiac function | coded_text | good contractility (normal)\|mildly impaired left ventricular contractility |  |
|  |  |  |  |  | OBX HeartFetus.CardiacPosition | Cardiac position | coded_text | normal |  |
|  |  |  |  |  | OBX HeartFetus.CardiacProportions | Cardiac proportions | coded_text | proportioned (normal)\|disproportioned |  |
|  |  |  |  |  | OBX HeartFetus.CardiacRhythm | Cardiac rhythm | coded_text | regular (normal) |  |
|  |  |  |  |  | OBX HeartFetus.CardiacSize | Cardiac size | coded_text | normal (approx. 1/3 of thoracic area)\|mildly increased |  |
|  |  |  |  |  | OBX HeartFetus.DescendingAortaDiameterZscoreMethod | Ao desc Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.FetalHeartRate | FHR | integer | 140 |  |
|  |  |  |  |  | OBX HeartFetus.GreatArteryCrossingDetails | Cross-over gr. arteries | free_text | anterior great artery (confirmed to be the pulmonary artery by its branching) which crosses the course of the proximal aorta, indicative of normal relationship of the great arteries |  |
|  |  |  |  |  | OBX HeartFetus.HeartAppearance | Heart | coded_text | abnormal\|suboptimal\|normal |  |
|  |  |  |  |  | OBX HeartFetus.HeartDetails | Heart | coded_text | Atrioventricular septal defect: Complete\|Ebstein anomaly |  |
|  |  |  |  |  | OBX HeartFetus.IntracardiacEchogenicFocusPrint | Echogenic focus print | coded_text | Print |  |
|  |  |  |  |  | OBX HeartFetus.LeftVentricularAreaZscoreMethod | LV area Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.LeftVentricularInletDiameterZscoreMethod | LV inlet Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.LeftVentricularWidthDiastole2DZscoreMethod | LV width diast Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.MVAnnulusOverTVAnnulusDiastole | MV annulus diast / TV annulus diast | decimal | 1.0813094 (1.08) |  |
|  |  |  |  |  | OBX HeartFetus.MitralValveAnnulusDiameterDiastole2D | MV annulus diast | decimal | 10.24 (10.2) |  |
|  |  |  |  |  | OBX HeartFetus.MitralValveAnnulusDiameterDiastole2DZscoreBPD | MV annulus diast Zscore (BPD) | decimal | 2.39964631 (2.40) |  |
|  |  |  |  |  | OBX HeartFetus.MitralValveAnnulusDiameterDiastole2DZscoreFL | MV annulus diast Zscore (FL) | decimal | 2.63252498 (2.63) |  |
|  |  |  |  |  | OBX HeartFetus.MitralValveAnnulusDiameterDiastole2DZscoreGA | MV annulus diast Zscore (GA) | decimal | 2.88866451 (2.89) |  |
|  |  |  |  |  | OBX HeartFetus.MitralValveAnnulusDiameterDiastole2DZscoreMethod | MV annulus diast Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.PericardialEffusion | Pericardial effusion | coded_text | no |  |
|  |  |  |  |  | OBX HeartFetus.PericardialEffusionPrint | Pericardial effusion print | coded_text | Print |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryArteryLBranchDiameterZscoreMethod | Lt PA branch Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryArteryLDetails | Lt branch PA | coded_text | normal |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryArteryMainDetails | Main PA | coded_text | normal size and bifurcation |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryArteryMainDiameterZscoreMethod | PA main Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryArteryRBranchDiameterZscoreMethod | Rt PA branch Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryArteryRDetails | Rt branch PA | coded_text | normal |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2D | PV annulus syst | decimal | 6.85 (6.9)\|10.33 (10.3) |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2DZscoreBPD | PV annulus syst Zscore (BPD) | decimal | 2.24627632 (2.25)\|6.55558603 (6.56) |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2DZscoreFL | PV annulus syst Zscore (FL) | decimal | 3.9262725 (3.93)\|7.02824005 (7.03) |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2DZscoreGA | PV annulus syst Zscore (GA) | decimal | 3.63356606 (3.63)\|7.03425837 (7.03) |  |
|  |  |  |  |  | OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2DZscoreMethod | PV annulus syst Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.RightVentricularAreaZscoreMethod | RV area Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.RightVentricularInletDiameterZscoreMethod | RV inlet Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.RightVentricularWidthDiastole2DZscoreMethod | RV width diast Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2D | TV annulus diast | decimal | 9.47 (9.5) |  |
|  |  |  |  |  | OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2DZscoreBPD | TV annulus diast Zscore (BPD) | decimal | 1.32092812 (1.32) |  |
|  |  |  |  |  | OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2DZscoreFL | TV annulus diast Zscore (FL) | decimal | 1.486418 (1.49) |  |
|  |  |  |  |  | OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2DZscoreGA | TV annulus diast Zscore (GA) | decimal | 1.99539972 (2.00) |  |
|  |  |  |  |  | OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2DZscoreMethod | TV annulus diast Zscore by | coded_text | Schneider |  |
|  |  |  |  |  | OBX HeartFetus.VenousAtrialConnectionsDetails | Venous-atrial connections | coded_text | normal |  |
|  |  |  |  |  | OBX HeartFetus.VentricleArteryConnectionsDetails | VA connections | coded_text | concordant |  |
|  |  |  |  |  | OBX HeartFetus.VentriclesDetails | Ventricles | coded_text | normal size and morphology |  |
|  |  |  |  |  | OBX HeartFetus.VisceroAtrialSitusAppearance | Situs | coded_text | situs solitus (normal) |  |
<!-- END: generated cluster=cardiac -->

### amniotic_fluid

Amniotic fluid index, single deepest pocket, and the GE amniotic-fluid measurement family.

_16 rows: 9 Observer, 7 HL7, 0 paired._

<!-- BEGIN: generated cluster=amniotic_fluid -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | fetuses[].amioticfluid.amniotic_fluid.afi_done |  | integer | 0\|1 |  |  |  |  |  |
|  | fetuses[].amioticfluid.amniotic_fluid.afi_total |  | decimal | 11.5 |  |  |  |  |  |
|  | fetuses[].amioticfluid.amniotic_fluid.amniotic_fluid_volume |  | coded_text | Normal |  |  |  |  |  |
|  | fetuses[].amioticfluid.amniotic_fluid.done |  | integer | 1 |  |  |  |  |  |
|  | fetuses[].amioticfluid.amniotic_fluid.largest_vertical_pocket |  | decimal\|integer | 5\|3.7 |  |  |  |  |  |
|  | fetuses[].amioticfluid.amniotic_fluid.percentile_for_display |  | percentile | 16% |  |  |  |  |  |
|  | fetuses[].amioticfluid.amniotic_fluid.quadrant_2 |  | decimal | 3.5 |  |  |  |  |  |
|  | fetuses[].amioticfluid.amniotic_fluid.quadrant_3 |  | decimal | 4.5 |  |  |  |  |  |
|  | fetuses[].amioticfluid.amniotic_fluid.quadrant_4 |  | decimal | 3.5 |  |  |  |  |  |
|  |  |  |  |  | OBX Fetus.AmnioticFluidAmount | Amniotic fluid | coded_text | oligohydramnios\|normal |  |
|  |  |  |  |  | OBX Fetus.AmnioticFluidMaximumVerticalPocket | MVP | decimal | 1.62 (1.6)\|2.03 (2.0)\|5.36 (5.4)\|4.6\|3.35 (3.4)\|4.27 (4.3) |  |
|  |  |  |  |  | OBX Fetus.VP_AmnioticFluidDetails_Mask |  | free_text | Normal amount with MVP of 5.4 cm\\.br\\\\.br\\ |  |
|  |  |  |  |  | OBX Fetus.VP_AmnioticFluidMaximumVerticalPocket_Author |  | coded_text | Magann |  |
|  |  |  |  |  | OBX Fetus.VP_AmnioticFluidMaximumVerticalPocket_DevRatio |  | decimal\|percentile | -65.5 (-65.5%)\|-52.9 (-52.9%)\|14 (+14.0%)\|-4.3 (-4.3%)\|-30.2 (-30.2%)\|-8.6 (-8.6%) |  |
|  |  |  |  |  | OBX Fetus.VP_AmnioticFluidMaximumVerticalPocket_Deviation |  | decimal | -3.2 (-3.2SD)\|-2.5 (-2.5SD)\|0.5 (+0.5SD)\|-0.2 (-0.2SD)\|-1.3 (-1.3SD)\|-0.4 (-0.4SD) |  |
|  |  |  |  |  | OBX Fetus.VP_AmnioticFluidMaximumVerticalPocket_Percentile |  | percentile | 0 (<1%)\|1 (<1%)\|70 (70%)\|43 (43%)\|9 (9%)\|34 (34%) |  |
<!-- END: generated cluster=amniotic_fluid -->

### placenta_cord

Placenta location and grading, umbilical cord findings, umbilical artery Doppler indices, and fetal-vessel data.

_151 rows: 119 Observer, 32 HL7, 0 paired._

<!-- BEGIN: generated cluster=placenta_cord -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | fetuses[].fetalvessels.ductus_venosus.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.ductus_venosus.ductus_venosus_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.ductus_venosus.peak_atrial_systolic |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.ductus_venosus.peak_ventricular_diastolic |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.ductus_venosus.peak_ventricular_systolic |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.ductus_venosus.reverse_flow |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fetalvessels.ductus_venosus.systolic_atrial_ratio |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.ductus_venosus.systolic_diastolic_ratio |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.intrahep_vein.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.intrahep_vein.pulsations |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.absent_end_diastolic_velocity |  | coded_text | ? |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.peak_systolic_velocity |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.peak_systolic_velocity_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.peak_systolic_velocity_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.peak_systolic_velocity_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.pulsatility_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.pulsatility_index_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.pulsatility_index_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.pulsatility_index_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.resistance_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.resistance_index_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.resistance_index_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.resistance_index_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.systolic_diastolic_ratio |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.systolic_diastolic_ratio_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.systolic_diastolic_ratio_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.middle_cerebral_artery.systolic_diastolic_ratio_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.pulsatility_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.pulsatility_index_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.pulsatility_index_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.pulsatility_index_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.resistance_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.resistance_index_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.resistance_index_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.resistance_index_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.systolic_diastolic_ratio |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.systolic_diastolic_ratio_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.systolic_diastolic_ratio_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.renal_artery.systolic_diastolic_ratio_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.absent_end_diastolic_velocity |  | coded_text | ? |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.peak_systolic_velocity |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.peak_systolic_velocity_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.peak_systolic_velocity_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.peak_systolic_velocity_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.pulsatility_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.pulsatility_index_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.pulsatility_index_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.pulsatility_index_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.resistance_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.resistance_index_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.resistance_index_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.resistance_index_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.reverse_flow |  | coded_text | ? |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.systolic_diastolic_ratio |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.systolic_diastolic_ratio_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.systolic_diastolic_ratio_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.thoracic_aorta.systolic_diastolic_ratio_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.absent_end_diastolic_velocity |  | coded_text | ? |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.pulsatility_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.pulsatility_index_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.pulsatility_index_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.pulsatility_index_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.resistance_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.resistance_index_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.resistance_index_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.resistance_index_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.reverse_flow |  | coded_text | ? |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.systolic_diastolic_ratio |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.systolic_diastolic_ratio_mom |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.systolic_diastolic_ratio_percentile |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_artery.systolic_diastolic_ratio_z_score |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_vein.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.umbilical_vein.pulsations |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.atrial_filling_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.peak_diastolic_flow |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.peak_reverse_flow |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.pi_reverse_over_pi_forward_ratio |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.pulsatility_index_forward |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.pulsatility_index_reverse |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.systolic_velocity_max |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.systolic_velocity_min |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_inferior.velocity_time_integral_systolic_wave |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.atrial_filling_index |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.peak_diastolic_flow |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.peak_reverse_flow |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.pi_reverse_over_pi_forward_ratio |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.pulsatility_index_forward |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.pulsatility_index_reverse |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.systolic_velocity_max |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.systolic_velocity_min |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetalvessels.vena_cava_superior.velocity_time_integral_systolic_wave |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].placenta.amnion_seen |  | coded_text | Unspecified\|Seen |  |  |  |  |  |
|  | fetuses[].placenta.anterior_pos |  | integer | 1\|0 |  |  |  |  |  |
|  | fetuses[].placenta.chor_amniotic |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].placenta.chor_chorionic |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].placenta.done |  | integer | 1 |  |  |  |  |  |
|  | fetuses[].placenta.echoluc |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].placenta.fundal_pos |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].placenta.grade |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].placenta.lft_lat_pos |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].placenta.low_lyng_pos |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].placenta.posterior_pos |  | integer | 0\|1 |  |  |  |  |  |
|  | fetuses[].placenta.previa |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].placenta.rht_lat_pos |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].placenta.subchor_sonoluc |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].placenta.thickness |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].placenta.thickness_user_spec |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].uards.uards.a_priori_risk |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].uards.uards.a_priori_risk_lookup |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].uards.uards.maternal_age_risk |  | integer | 22\|29\|37\|47\|61 |  |  |  |  |  |
|  | fetuses[].uards.uards.risk_adjustment |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].uards.uards.risk_adjustment_lookup |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].uards.uards.ultrasound_adjusted_risk |  | integer | 0 |  |  |  |  |  |
|  |  |  |  |  | OBX Fetus.PlacentaSite | Placenta | coded_text | anterior |  |
|  |  |  |  |  | OBX Fetus.VP_PlacentaDetails_Mask |  | free_text | left lateral\\.br\\\\.br\\\|anterior\\.br\\\\.br\\\|posterior, fundal\\.br\\\\.br\\\|posterior\\.br\\\\.br\\ |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.CordVessels | Cord vessels | coded_text | 3 vessel cord |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.UmbilicalArteryUndefinedEDV | Umbilical A ED | decimal | 19.5 (19.50) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.UmbilicalArteryUndefinedHR | Umbilical A HR | integer | 201 |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.UmbilicalArteryUndefinedMD | Umbilical A MD | decimal | 19.21 |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.UmbilicalArteryUndefinedPI | Umbilical A PI | decimal | 0.86 |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.UmbilicalArteryUndefinedPSV | Umbilical A PS | decimal | 42.72 |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.UmbilicalArteryUndefinedRI | Umbilical A RI | decimal | 0.54 |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.UmbilicalArteryUndefinedSoverD | Umbilical A S / D | decimal | 2.19 |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.UmbilicalArteryUndefinedTAmax | Umbilical A TAmax | decimal | 27.08 |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPI_Author |  | coded_text | Baschat |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPI_DevRatio |  | percentile | -20.9 (-20.9%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPI_Deviation |  | decimal | -1.4 (-1.4SD) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPI_Percentile |  | percentile | 9 (9%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPSV_Author |  | coded_text | Ebbing |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPSV_DevRatio |  | percentile | -1.8 (-1.8%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPSV_Deviation |  | decimal | -0.1 (-0.1SD) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPSV_Percentile |  | percentile | 45 (45%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedRI_Author |  | coded_text | Schaffer |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedRI_DevRatio |  | percentile | -21.3 (-21.3%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedRI_Deviation |  | decimal | -1.8 (-1.8SD) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedRI_Percentile |  | percentile | 4 (4%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedSoverD_Author |  | coded_text | Acharya |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedSoverD_DevRatio |  | percentile | -27.1 (-27.1%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedSoverD_Deviation |  | decimal | -1.5 (-1.5SD) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedSoverD_Percentile |  | percentile | 7 (7%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedTAmax_Author |  | coded_text | Ebbing |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedTAmax_DevRatio |  | percentile | -4.1 (-4.1%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedTAmax_Deviation |  | decimal | -0.3 (-0.3SD) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedTAmax_Percentile |  | percentile | 39 (39%) |  |
|  |  |  |  |  | OBX UmbilicalCordFetus.VP_UmbilicalCordDetails_Mask |  | free_text | 3 vessel cord\\.br\\\\.br\\\|2 vessel cord\\.br\\\\.br\\ |  |
<!-- END: generated cluster=placenta_cord -->

### fetal_procedures

Invasive fetal procedures: amniocentesis, FBS/CVS, ectopic pregnancy management, other procedures.

_41 rows: 41 Observer, 0 HL7, 0 paired._

<!-- BEGIN: generated cluster=fetal_procedures -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | fetuses[].amniocentesis.amniocentesis.attempts |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.cc_fluid_wd |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.comps |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.fluid_char |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.needle_gauge |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.post_procedure_fetal_heart_motion |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.post_procedure_rh_factor |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.post_procedure_rhogam_admin |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.trans_plac |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].amniocentesis.amniocentesis.us_guidance |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].ectopic_preg.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].ectopic_preg.ect_loc |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].ectopic_preg.ect_size_a |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].ectopic_preg.ect_size_b |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].ectopic_preg.ect_size_c |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.attempts |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.comps |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.mg_of_villi |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.needle_gauge |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.trans_abd_cvs |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.trans_cx_cvs |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.trans_plac |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.us_guidance |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.cvs.villi_ob |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.attempts |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.cc_blood_wd |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.comps |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.needle_gauge |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.samp_site |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.samp_site_txt |  | empty |  |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.trans_plac |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fbscvs.fetal_blood_sampling.us_guidance |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].otherprocs.fetal_reduction.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].otherprocs.fetal_reduction.outcome |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].otherprocs.fetal_reduction.type |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].otherprocs.fetal_transfusion.done |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].otherprocs.fetal_transfusion.success |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].otherprocs.fetal_transfusion.type |  | coded_text | Unspecified |  |  |  |  |  |
<!-- END: generated cluster=fetal_procedures -->

### fetus_core

Per-fetus identity (number, position, presentation, tone, activity), antepartum testing (NST, BPP).

_37 rows: 34 Observer, 4 HL7, 1 paired._

<!-- BEGIN: generated cluster=fetus_core -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | fetuses[].bpp.afv |  | integer | 0\|2 |  |  |  |  |  |
|  | fetuses[].bpp.breathing |  | integer | 0\|2 |  |  |  |  |  |
|  | fetuses[].bpp.mvmnt |  | integer | 0\|2 |  |  |  |  |  |
|  | fetuses[].bpp.nst |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].bpp.tone |  | integer | 0\|2 |  |  |  |  |  |
|  | fetuses[].bpp.total |  | integer | 0\|8 |  |  |  |  |  |
|  | fetuses[].fetus.anatomy_text |  | coded_text\|free_text | The cerebellum appeared abnormal. Please see anatomy comments for further details. The fetal face appears normal. Anatomy of the fetal thorax appeared within normal limits. The cardiac size and structures appeared sonographically normal at the four chamber view, and cardiac rhythm was regular. The abdominal cavity appears normal. The fetal stomach appears normal. The right kidney appears within normal limits with respect to size, collection systems, and parenchyma. The left kidney appears within normal limits with respect to size, collection systems, and parenchyma. The fetal bladder appears normal. The abdominal wall appears intact. The spine was visualized from cervical to sacral region, within the resolution of the ultrasound equipment, without evidence of a neural tube defect. Active movement of the extremities was seen and fetal body motion was also observed during this examination. Normal genitalia. The placenta appears within normal limits. There is a 3 vessel cord with normal insertion site.\|The fetal cranium appeared normal in shape. The choroid plexus was well visualized, the lateral ventricles were not dilated and the midline structures were not deviated. The cerebellum and cisterna magna were visualized and appeared normal. The fetal face appears normal. Anatomy of the fetal thorax appeared within normal limits. The cardiac size and structures appeared sonographically normal at the four chamber view, and cardiac rhythm was regular. The abdominal cavity appears normal. The fetal stomach appears normal. Abnormalities were noted in the right kidney:  please see the anatomy comments for further details. The left kidney appears within normal limits with respect to size, collection systems, and parenchyma. The fetal bladder appears normal. The abdominal wall appears intact. The spine was visualized from cervical to sacral region, within the resolution of the ultrasound equipment, without evidence of a neural tube defect. Active movement of the extremities was seen and fetal body motion was also observed during this examination. Normal genitalia. The placenta appears within normal limits. There is a 3 vessel cord with normal insertion site.\|The fetal cranium appeared normal in shape. The choroid plexus was well visualized, the lateral ventricles were not dilated and the midline structures were not deviated. The cerebellum and cisterna magna were visualized and appeared normal. The fetal face appears normal. Anatomy of the fetal thorax appeared within normal limits. The cardiac position was not evaluated.         The abdominal cavity appears normal. The fetal stomach appears normal. The right kidney appears within normal limits with respect to size, collection systems, and parenchyma. The left kidney appears within normal limits with respect to size, collection systems, and parenchyma. The fetal bladder appears normal. Abnormal abdominal wall: please see the anatomy comments for further details. The spine was visualized from cervical to sacral region, within the resolution of the ultrasound equipment, without evidence of a neural tube defect. The left forearm appeared normal. The right humerus appeared normal. The left humerus appeared normal. The right forearm appeared normal. The right foot appeared normal. The left foot appeared normal. The right lower leg appeared normal. The left lower leg appeared normal. The right femur appeared normal. The left femur was not evaluated. The right hand appeared normal. The left hand  appeared normal. Normal genitalia. The placenta appears within normal limits. There is a 3 vessel cord with normal insertion site.\|The calvarium was abnormal. Please see anatomy comments for details.\|The fetal cranium appeared normal in shape. The choroid plexus was well visualized, the lateral ventricles were not dilated and the midline structures were not deviated. The cerebellum and cisterna magna were visualized and appeared normal. The fetal face appears normal. Anatomy of the fetal thorax appeared within normal limits. The four chamber view appeared abnormal. Please see anatomy comments for further details.        The abdominal cavity appears normal. The fetal stomach appears normal. The right kidney appears within normal limits with respect to size, collection systems, and parenchyma. The left kidney appears within normal limits with respect to size, collection systems, and parenchyma. The fetal bladder appears normal. The abdominal wall appears intact. The fetal spine was not visualized on today's exam due to fetal position. The fetal extremities were not assessed on today's exam. Normal genitalia. The placenta appears within normal limits. There is a 3 vessel cord with normal insertion site. |  |  |  |  |  |
|  | fetuses[].fetus.echo_text |  | empty |  |  |  |  |  |  |
|  | fetuses[].fetus.estimated_fetal_weight |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetus.fetal_echo_cardiac_axis_degrees |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetus.fetal_echo_performed |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetus.fetus_death |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetus.fetus_growth |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fetus.fetus_number |  | integer | 1 |  |  |  |  |  |
|  | fetuses[].fetus.fetus_presentation |  | coded_text | Vertex\|Breech\|Unspecified |  |  |  |  |  |
|  | fetuses[].fetus.fetus_reduced |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].fetus.fetus_seen |  | integer | 1 |  |  |  |  |  |
|  | fetuses[].fetus.ga_by_sonography |  | decimal\|integer | 27\|23.4\|36.1\|11.3\|28.4 |  |  |  |  |  |
| fetus.gender | fetuses[].fetus.gender |  | coded_text | Unspecified | OBX BabyPatientData.Gender | Fetal sex | coded_text | normal |  |
|  | fetuses[].fetus.impression_text |  | free_text | Singleton IUPRegular fetal heart rate of 150 bpmAnterior placenta27 weeks and 0 days by this ultrasound. (EDD = OCT 1 2025)26 weeks and 4 days by 1st Trimester Sono. (EDD = OCT 4 2025)Estimated Fetal Weight = 1015 grams Hadlock 85 (AC, FL, HC)Estimated Fetal Weight = 2 lbs 4 oz Hadlock 85 (AC, FL, HC)Dandy Walker\|Singleton IUPRegular fetal heart rate of 150 bpmAnterior placenta23 weeks and 3 days by this ultrasound. (EDD = FEB 16 2026)23 weeks and 4 days by Other. (EDD = OCT 25 2025)Estimated Fetal Weight = 598 grams Hadlock 85 (AC, FL, HC)Estimated Fetal Weight = 1 lbs 5 oz Hadlock 85 (AC, FL, HC)Renal agenesis\|Singleton IUPRegular fetal heart rate of 150 bpmPosterior placenta36 weeks and 1 day by this ultrasound. (EDD = JUL 29 2025)35 weeks and 5 days by Other. (EDD = AUG 1 2025)Estimated Fetal Weight = 2778 grams Hadlock 85 (AC, FL, HC)Estimated Fetal Weight = 6 lbs 2 oz Hadlock 85 (AC, FL, HC)Omphalocele\|Singleton IUPRegular fetal heart rate of 161 bpmPosterior placenta11 weeks and 2 days by this ultrasound. (EDD = JAN 20 2026)11 weeks and 0 days by 1st Trimester Sono. (EDD = JAN 22 2026)Acrania\|Singleton IUPRegular fetal heart rate of 150 bpmPosterior placenta28 weeks and 3 days by this ultrasound. (EDD = SEP 22 2025)28 weeks and 0 days by 2nd Trimester Sono. (EDD = SEP 25 2025)Estimated Fetal Weight = 1274 grams Hadlock 85 (AC, FL, HC)Estimated Fetal Weight = 2 lbs 13 oz Hadlock 85 (AC, FL, HC)Hypoplastic left ventricle |  |  |  |  |  |
|  | fetuses[].fetus.multi_fetus_position_anterior_posterior |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fetus.multi_fetus_position_left_right |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fetus.multi_fetus_position_supine |  | coded_text | Unspecified |  |  |  |  |  |
|  | fetuses[].fetus.use_early_anatomy_text |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].impression.fetus_anomalies[].abnom_or_nrml_var |  | integer | 2 |  |  |  |  |  |
|  | fetuses[].impression.fetus_anomalies[].descr |  | coded_text | Dandy Walker\|Renal agenesis\|Omphalocele\|Acrania\|Hypoplastic left ventricle |  |  |  |  |  |
|  | fetuses[].impression.fetus_anomalies[].fh_rec_no |  | integer | 451676\|452064\|452450\|452836\|453216 |  |  |  |  |  |
|  | fetuses[].nst.decels_late |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].nst.decels_pro |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].nst.decels_var |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].nst.reactive |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].nst.spont_hyperstim |  | integer | 0 |  |  |  |  |  |
|  | fetuses[].nst.time_end |  | empty |  |  |  |  |  |  |
|  | fetuses[].nst.time_start |  | empty |  |  |  |  |  |  |
|  |  |  |  |  | OBX Fetus.Identifier | Fetus Identifier | coded_text | A |  |
|  |  |  |  |  | OBX Fetus.Movements | Fetal movements | coded_text | movement and tone |  |
|  |  |  |  |  | OBX Fetus.Presentation | Presentation | coded_text | transverse \|cephalic\|oblique superior\|transverse |  |
<!-- END: generated cluster=fetus_core -->

### indication_impression

Free-text and coded exam indications, ICD-10 codes, and narrative impressions.

_8 rows: 2 Observer, 8 HL7, 2 paired._

<!-- BEGIN: generated cluster=indication_impression -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| indication.code | exam.examIcd10Indication[].code |  | coded_text | Z36.1\|O09.529\|O09.519 | OBX CodingDiagnosis.Code | Code | coded_text | Z3A.24\|O76\|O35.9XX0\|Z3A.19\|Z3A.13\|Z36.82\|O35.BXX0\|Z3A.32\|O35.EXX0\|Z3A.28\|... |  |
| indication.description | exam.examIcd10Indication[].description |  | coded_text | Encounter for antenatal screening for raised alphafetoprotein level\|Supervision of elderly multigravida, unspecified trimester\|Supervision of elderly primigravida, unspecified trimester | OBX CodingDiagnosis.Description | Description | coded_text\|free_text | Weeks of gestation\|Abnormality in fetal heart rate and rhythm complicating labor and delivery\|Maternal care for (suspected) fetal abnormality and damage, unspecified\|Encounter for Nuchal Translucency Screening\|Maternal care for other (suspected) fetal abnormality and damage, fetal cardiac anomalies\|UTD (pyelectasis) found\|Maternal care for known or suspected placental insufficiency |  |
|  |  |  |  |  | OBX Coding.AutoAcceptanceAlreadyPerformed | Auto acceptance | coded_text | true |  |
|  |  |  |  |  | OBX CodingProcedure.Code | Code | integer | 76816\|76825\|76827\|93325\|76811\|76801\|76813\|76820 |  |
|  |  |  |  |  | OBX CodingProcedure.Description | Description | coded_text\|free_text | Ultrasound, pregnant uterus, real time with image documentation, follow up, transabdominal approach per fetus\|Echocardiography, fetal, cardiovascular system, real time with image documentation (2D), with or without M-mode recording\|Doppler echocardiography, pulsed wave and/or continuous wave with spectral display; complete\|Doppler echocardiography color flow velocity mapping\|Ultrasound, pregnant uterus, real time with image documentation, fetal and maternal evaluation plus detailed fetal anatomic examination, transabdominal approach;single or first gestation\|Ultrasound, pregnant uterus, real time with image documentation, fetal and maternal evaluation, first trimester (< 14 weeks 0 days), transabdominal approach; single or first gestation\|Ultrasound, pregnant uterus, real time with image documentation, first trimester fetal nuchal translucency measurement, transabdominal or transvaginal approach; single or first gestation\|Doppler velocimetry, fetal; umbilical artery |  |
|  |  |  |  |  | OBX ExamAddData.ExamImpression | Impression | free_text | The patient is referred for a fetal echocardiogram with multiple anomalies noted.. \\.br\\\\.br\\The fetal biometry is consistent with gestational dating derived from her menstrual history. The estimated fetal weight is 652 g at the 42%. Fetal movement and tone are observed. Oligohydramnios is noted with a single deepest pocket of 1.6 cm. \\.br\\\\.br\\Multiple anomalies are noted including"\\.br\\-Abnormal head shape (brachycephaly)\\.br\\-Bilateral ventriculomegaly\\.br\\-Major CHD consistent with AVSD and pulmonary stenosis.\\.br\\\\.br\\The patient is informed of the findings. She is counseled about the limitations of the exam in detecting all forms of fetal congenital abnormalities. \|The patient is referred for a detailed morphology ultrasound for the detection of fetal anomalies. \\.br\\\\.br\\The fetal biometry is consistent with gestational dating derived from her menstrual history. Fetal movement and tone are observed. The amniotic fluid volume appears normal with a single deepest pocket of 2 cm. \\.br\\\\.br\\Multiple anomalies are noted including"\\.br\\-Abnormal head shape (brachycephaly)\\.br\\-Bilateral ventriculomegaly\\.br\\-Thickened nuchal fold\\.br\\-Major CHD consistent with AVSD.\\.br\\\\.br\\The patient is informed of the findings. She is counseled about the limitations of the exam in detecting all forms of fetal congenital abnormalities. \|This patient is referred for a detailed first trimester ultrasound for the early detection of fetal anomalies including the nuchal translucency measurement.\\.br\\ \\.br\\Transabdominal  images reveal a single intrauterine gestation with positive cardiac activity noted. Fetal crown rump length measurements are consistent with gestational dating derived from today's scan. Fetal movement is noted. The fetal anatomy appears normal for this gestational age; please see comments above for full details. \\.br\\\\.br\\A cystic hygroma is noted. The nuchal translucency measures 4 mm at the >99%.\\.br\\ \\.br\\The patient is informed of the findings. She is counseled about the limitations of the exam in detecting all forms of fetal congenital abnormalities. \|This patient is referred for a fetal echocardiogram with suspected cardiac anomaly.\\.br\\\\.br\\The fetal biometry is consistent with gestational dating derived from her stated EDD. The estimated fetal weight is 679 g at the 54%. The amniotic fluid volume appears normal with a single deepest pocket of 5.4 cm. The fetal anatomy appears normal. \\.br\\\\.br\\A 2-vessel umbilical cord is noted.\\.br\\\\.br\\Detailed evaluation of fetal cardiac structure and function reveals a major CHD consistent with Ebstein's anomaly; please see comments above for full details.\\.br\\\\.br\\The patient is informed of the findings. She is counseled about the limitations of the ultrasound exam in detecting all forms of fetal congenital cardiac abnormalities. \|This patient is referred for interval fetal growth with UTD noted on an outside scan.\\.br\\\\.br\\The fetal biometry is consistent with gestational dating derived from her stated EDD. The estimated fetal weight is 1942 g, at the 36%. Fetal movement and tone are observed. The amniotic fluid volume appears normal with a single deepest pocket of 4.6 cm. \\.br\\\\.br\\Urinary tract dilation (UTD A2-3) is noted in the right kidney measuring 11.2 mm and in the left kidney measuring 13.4 mm. The renal parenchyma appears normal in size and echogenicity. Normal bladder filling is noted without evidence of ureterocele or ureter dilation. UTD occurs in 1% to 2% of pregnancies and is most commonly a transient finding that is a normal variant. UTD may indicate renal or urinary tract pathology and may also be a marker of Trisomy 21. The association between Trisomy 21 and UTD has been well described in several series, and the finding of UTD confers a positive LR of 1.5, suggesting a minimal risk. For pregnant patients with negative serum or cfDNA screening results and isolated UTD, we recommend no further aneuploidy evaluation. For fetuses with isolated UTD A1, we recommend an ultrasound examination at about 32 weeks of gestation and pediatric urology consultation. For fetuses with UTD A2-3, we recommend ultrasound assessment every 4-6 weeks and pediatric urology. \\.br\\\\.br\\The patient is informed of the findings. She is counseled about the limitations of the ultrasound exam in detecting all forms of fetal congenital cardiac abnormalities. \|This patient is referred for interval fetal growth with FGR.\\.br\\\\.br\\The fetal biometry is consistent with gestational dating derived from her stated EDD. The estimated fetal weight is 918 g, at the 3%. Fetal movement and tone are observed. The amniotic fluid volume appears normal with a single deepest pocket of 3.4 cm. \\.br\\\\.br\\Doppler velocimetry evaluation of the umbilical artery is within normal limits for this gestational age. \\.br\\\\.br\\The patient is informed of the findings. She is counseled about the limitations of the ultrasound exam in detecting all forms of fetal congenital cardiac abnormalities. \|The patient is referred for a detailed morphology ultrasound for the detection of fetal anomalies. \\.br\\\\.br\\The fetal biometry is consistent with gestational dating derived from her menstrual history. Fetal movement and tone are observed. The amniotic fluid volume appears normal with a single deepest pocket of 4.3 cm. \\.br\\\\.br\\Today's findings include:\\.br\\- Abnormal skull shape (cloverleaf)\\.br\\- Right lateral ventriculomegaly\\.br\\- Hypoplasia of the cerebellum\\.br\\\\.br\\The patient is informed of the findings. She is counseled about the limitations of the exam in detecting all forms of fetal congenital abnormalities.  |  |
|  |  |  |  |  | OBX ExamAddData.ExamRecommendation | Follow-up | coded_text | We recommend a follow up scan only as clinically indicated. \|A fetal echocardiogram is scheduled in 4 weeks.\|A morphology scan is scheduled\|We recommend a follow-up scan only as clinically indicated. |  |
|  |  |  |  |  | OBX ExamCodingIndication.Indication | Indication | coded_text | Known or suspected fetal anomaly\|Fetal Distress, Known or Suspected\|Encounter for Nuchal Translucency Screening\|Known fetal cardiac abnormality\|UTD (pyelectasis) found\|Fetal Growth Restriction |  |
<!-- END: generated cluster=indication_impression -->

### dating

Pregnancy dating: LMP, EDD, gestational age, agreed dating method.

_17 rows: 5 Observer, 12 HL7, 0 paired._

<!-- BEGIN: generated cluster=dating -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | exam.age_at_menopause |  | integer | 0 |  |  |  |  |  |
|  | exam.ga_by_dates |  | integer | 0 |  |  |  |  |  |
|  | exam.ga_by_working_edd |  | decimal\|integer | 26.6\|23.6\|35.7\|11\|28 |  |  |  |  |  |
|  | exam.lmp |  | date | 0001-01-01 |  |  |  |  |  |
|  | exam.pt_age_at_edd |  | integer | 45\|44\|43\|42\|41 |  |  |  |  |  |
|  |  |  |  |  | OBX AntenatalBookingHistory.EDDAgreed | Assigned EDD | date | 20260113\|20251030\|20250901\|20251001\|20251101 |  |
|  |  |  |  |  | OBX EpisodeHistory.AgreedDatingString | Assigned | coded_text | based on ultrasound (CRL), selected on 07/10/2025\|based on stated EDD, selected on 07/10/2025 |  |
|  |  |  |  |  | OBX EpisodeHistory.DefaultLengthofPregnancy | Pregnancy length | integer | 280 |  |
|  |  |  |  |  | OBX EpisodeHistory.EDDAgreed | Assigned EDD | date | 20260113\|20251030\|20250901\|20251001\|20251101 |  |
|  |  |  |  |  | OBX EpisodeHistory.EDDbyStatedDating | EDD by prior assessment | date | 20251030\|20250901\|20251001\|20251101 |  |
|  |  |  |  |  | OBX ExamOBDating.DateOfUltrasoundExamination | Ultrasound examination on | date | 20250923\|20250820\|20250710 |  |
|  |  |  |  |  | OBX ExamOBDating.EDDCurrentUltrasoundFetus1 | EDD by U/S | date | 20260107\|20260117\|20260113\|20251024\|20250904\|20251013\|20251106 |  |
|  |  |  |  |  | OBX ExamOBDating.GestationalAgeDaysAgreed | Assigned GA (weeks days) | weeks_days | 168 (24w 0d)\|134 (19w 1d)\|93 (13w 2d)\|227 (32w 3d)\|197 (28w 1d)\|166 (23w 5d) |  |
|  |  |  |  |  | OBX ExamOBDating.GestationalAgeDaysStatedDating | GA by prior assessment | weeks_days | 168 (24w 0d)\|227 (32w 3d)\|197 (28w 1d)\|166 (23w 5d) |  |
|  |  |  |  |  | OBX ExamOBDating.GestationalAgeDaysUltrasoundFetus1 | GA by U/S | weeks_days | 174 (24w 6d)\|130 (18w 4d)\|93 (13w 2d)\|224 (32w 0d)\|185 (26w 3d)\|161 (23w 0d) |  |
|  |  |  |  |  | OBX ExamOBDating.MethodOfDating | Method of dating | coded_text | based on ultrasound\|based on stated EDD |  |
|  |  |  |  |  | OBX ExamOBDating.MethodOfDatingUSIncludedParameterFetus1 | GA by U/S based upon | coded_text | AC, BPD, Femur, HC\|AC, BPD, Femur\|CRL |  |
<!-- END: generated cluster=dating -->

### maternal_subject

Maternal demographics and history: patient block, obstetric history, family/anamnestic history, antenatal booking, screening tests.

_34 rows: 27 Observer, 11 HL7, 4 paired._

<!-- BEGIN: generated cluster=maternal_subject -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | exam.ob_gyn_history.ect_preg_num_left |  | integer | 0 |  |  |  |  |  |
|  | exam.ob_gyn_history.ect_preg_num_other |  | integer | 0 |  |  |  |  |  |
|  | exam.ob_gyn_history.ect_preg_num_right |  | integer | 0 |  |  |  |  |  |
|  | exam.ob_gyn_history.f_term |  | integer | 0 |  |  |  |  |  |
| maternal.gravida | exam.ob_gyn_history.gravida |  | integer | 0 | OBX PatientAnamnesticData.Gravida | Gravida | integer | 1 |  |
|  | exam.ob_gyn_history.liv_children |  | integer | 0 |  |  |  |  |  |
|  | exam.ob_gyn_history.p_term |  | integer | 0 |  |  |  |  |  |
| maternal.para | exam.ob_gyn_history.para |  | integer | 0 | OBX PatientAnamnesticData.Para | Para | integer | 0 |  |
|  | exam.ob_gyn_history.s_abort |  | integer | 0 |  |  |  |  |  |
|  | exam.ob_gyn_history.stl_born |  | integer | 0 |  |  |  |  |  |
|  | exam.ob_gyn_history.t_abort |  | integer | 0 |  |  |  |  |  |
|  | exam.patient.b_date |  | date | 1980-04-01\|1981-05-02\|1982-06-03\|1983-07-04\|1984-08-05 |  |  |  |  |  |
| maternal.first_name | exam.patient.first_name |  | coded_text | Sally | OBX PatientHistory.FirstName | First name | coded_text | Test5\|Test4\|Test3\|Test2\|Test1 |  |
| maternal.last_name | exam.patient.last_name |  | coded_text | Apple\|Blue\|Charm\|Diva\|Eclair | OBX PatientHistory.Name | Last name | coded_text | Phenotype |  |
|  | exam.pt_age_at_exam |  | integer | 45\|44\|43\|41\|40 |  |  |  |  |  |
|  | hist_phys_vitals.surgeries |  | empty |  |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.bmi |  | decimal\|integer | 0\|25\|29.3 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.height_feet |  | integer | 0\|5 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.height_inches |  | integer | 0\|5\|7 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.initial_blood_pressure_dia |  | integer | 0 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.initial_blood_pressure_sys |  | integer | 0 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.initial_plood_uressurelse |  | integer | 0 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.later_bp_dia |  | integer | 0 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.later_bp_sys |  | integer | 0 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.later_pulse |  | integer | 0 |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.time_vitals_rec_init |  | empty |  |  |  |  |  |  |
|  | hist_phys_vitals.vital_signs.weight_lb |  | integer | 0\|150\|187 |  |  |  |  |  |
|  |  |  |  |  | OBX MaternalScreeningTests.Print | Print | coded_text | Print |  |
|  |  |  |  |  | OBX PatientFamilyHistory.PatientFamilyHistoryDetails | Details | coded_text | spina bifida |  |
|  |  |  |  |  | OBX PatientFamilyHistory.Print | Print | coded_text | Print |  |
|  |  |  |  |  | OBX PatientFamilyHistory.RelativeHistory | Relative | coded_text | Father |  |
|  |  |  |  |  | OBX PatientHistory.Country | Country | coded_text | USA |  |
|  |  |  |  |  | OBX PatientHistory.DOB | DOB | date | 20010101 |  |
|  |  |  |  |  | OBX PatientHistory.Sex | Sex | coded_text | unknown |  |
<!-- END: generated cluster=maternal_subject -->

### encounter

Exam-level metadata: date, location, signing, exam type, referring provider, accession, plus GE imaging-parameter and structured-report file blocks.

_54 rows: 21 Observer, 33 HL7, 0 paired._

<!-- BEGIN: generated cluster=encounter -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | exam.accession_id |  | empty |  |  |  |  |  |  |
|  | exam.disc_perc |  | integer | 0 |  |  |  |  |  |
|  | exam.examHL7Orders |  | empty |  |  |  |  |  |  |
|  | exam.examReferring[].assgnd_id |  | integer | 16 |  |  |  |  |  |
|  | exam.examReferring[].name |  | coded_text | Ronald Wapner |  |  |  |  |  |
|  | exam.examTypes |  | empty |  |  |  |  |  |  |
|  | exam.exm_date |  | date | 2025-07-02\|2025-07-03 |  |  |  |  |  |
|  | exam.exm_locator |  | coded_text | AP10174-U-1-1\|BL10175-U-1-1\|CH10176-U-1-1\|DI10177-U-1-1\|EC10178-U-1-1 |  |  |  |  |  |
|  | exam.exm_signed |  | integer | 1 |  |  |  |  |  |
|  | exam.fetus_count |  | integer | 1 |  |  |  |  |  |
|  | exam.scope_name |  | coded_text | Limited OB Exam |  |  |  |  |  |
|  | exam.site_name |  | coded_text | 51 W51st Street |  |  |  |  |  |
|  | finalize.attendingMD.assgnd_id |  | integer | 30 |  |  |  |  |  |
|  | finalize.attendingMD.examiner_no |  | integer | 3 |  |  |  |  |  |
|  | finalize.attendingMD.name |  | coded_text | Ivette Miranda |  |  |  |  |  |
|  | finalize.examIcd10Diagnosis |  | empty |  |  |  |  |  |  |
|  | finalize.examinerTwo.assgnd_id |  | integer | 30 |  |  |  |  |  |
|  | finalize.examinerTwo.examiner_no |  | integer | 2 |  |  |  |  |  |
|  | finalize.examinerTwo.name |  | coded_text | Ivette Miranda |  |  |  |  |  |
|  | finalize.generalComment.formatted_text |  | empty |  |  |  |  |  |  |
|  | finalize.generalComment.plain_text |  | free_text | The patient was referred for a fetal anatomical survey.  Sonographic measurements were consistent with the expected gestational age. The amniotic fluid volume was normal. A detailed fetal anatomic survey was performed. The sonogram was significant for splaying of the cerebellar hemispheres. There was evidence of a cyst measuring __ connecting with the fourth ventricle. This is consistent with a Dandy-Walker malformation. The remainder of the fetal anatomy seen appeared normal within the resolution of the ultrasound. There was no evidence of macrocephaly, ventriculomegaly or agenesis of the corpus callosum.Due to the limited visualization of the cervix by the transabdominal approach, it was necessary to perform a transvaginal ultrasound. Transvaginal sonogram revealed a long, closed cervix. There were no changes noted with the Valsalva maneuver. A chaperone was present for the transvaginal ultrasound.The patient should be informed of the findings and counseled about the limitations of the exam. Although the absence of any sonographic markers reduces the likelihood of fetal aneuploidy, a normal ultrasound exam cannot exclude abnormal fetal genetics; definitive determination requires diagnostic genetic testing. Thank you for involving us in the care of the patient.\|The patient was referred for a fetal anatomical survey.Sonographic measurements were consistent with the expected gestational age. A detailed fetal anatomic survey was performed and revealed a normal left kidney with a an empty right renal fossa. The right kidney was not visualized and suggest a unilateral renal agenesis.  Color Doppler were used to identified a left renal artery and an absent right renal artery to confirm the diagnosis.  The amniotic fluid was subjectively normal. The rest of the fetal anatomy seen appeared normal within the resolution of the ultrasound. The patient was counseled that this finding has a low risk of anuploidy. There will be a risk of left renal hypertrophy by a compensatory contralateral kidney. She understands that unilateral renal agenesis is associated with Mullerian anomalies in about 40% of  the females with possible unicornuate or bicornuate uterus. Although ultrasound is an effective screening tool, it cannot exclude all congenital anomalies or genetic syndromes. The patient needs a  fetal echo and Pediatric Urology consult. A follow-up ultrasound is advised in 4-6 weeks to reassess fetal growth. Thank you for involving us in the care of the patient.\|The patient was referred for a fetal anatomical survey.  The fetus was appropriately grown and the amniotic fluid volume was normal. An abdominal wall defect consistent with a omphalocele was noted on today's exam.Omphalocele is a condition in which a baby's abdominal organs develop outside their belly. Babies with an omphalocele may also have other health conditions. The exam, however, was limited and all of the anatomical structures could not be satisfactorily visualized.  Due to the limited visualization of the cervix by the transabdominal approach, it was necessary to perform a transvaginal ultrasound. Transvaginal sonogram revealed a long, closed cervix. There were no changes noted with the Valsalva maneuver. A chaperone was present for the transvaginal ultrasound.The patient should be informed of the findings and counseled about the limitations of the exam. Although the absence of any sonographic markers reduces the likelihood of fetal aneuploidy, a normal ultrasound exam cannot exclude abnormal fetal genetics; definitive determination requires diagnostic genetic testing. A follow up exam is recommended prior to 23 weeks to complete the anatomical survey and to increase the detection rate of malformations diagnosed prenatally. Thank you for this referral.\|The patient was seen today for confirmation of pregnancy dating and nuchal translucency measurement. This is an IVF pregnancy with BMI of 33.8Transabdominal sonography was performed and revealed a singleton live intrauterine gestation. Due to limited visualization of the pregnancy transabdominally, a transvaginal exam was performed. The transvaginal exam confirmed the presence of a singleton live intrauterine gestation. Sonographic measurements were consistent with assigned gestational age. A normal fetal heart rate was noted. The amniotic fluid volume appeared normal. Views of the fetal head were suspicious for a cranial anomaly. Specifically, absence of the cranial vault and distortion of the brain is suspected, suggestive of acrania.The uterus and both ovaries were visualized and appeared normal.  No adnexal masses were noted.A follow-up scan is recommended between 11-14 weeks for the nuchal translucency assessment and early anatomy. The patient should also be counseled regarding options for aneuploidy screening and diagnostic testing if not done previously. Thank you for the referral.\|The patient was referred for a fetal anatomical survey.  The fetus was appropriately grown and the amniotic fluid volume was normal. Views of the fetal heart were suspicious for a cardiac anomaly. Specifically, a small ascending aorta, and a small but thick-walled left ventricle and enlarged right heart chambers were visualized.The exam, however, was limited and all of the anatomical structures could not be satisfactorily visualized.  Due to the limited visualization of the cervix by the transabdominal approach, it was necessary to perform a transvaginal ultrasound. Transvaginal sonogram revealed a long, closed cervix. There were no changes noted with the Valsalva maneuver. A chaperone was present for the transvaginal ultrasound.The patient should be informed of the findings and counseled about the limitations of the exam. Although the absence of any sonographic markers reduces the likelihood of fetal aneuploidy, a normal ultrasound exam cannot exclude abnormal fetal genetics; definitive determination requires diagnostic genetic testing. A follow up exam is recommended prior to 23 weeks to complete the anatomical survey and to increase the detection rate of malformations diagnosed prenatally. Thank you for this referral. |  |  |  |  |  |
|  |  |  |  |  | OBX EpisodeHistory.NumberOfFetuses | Number of gestational sacs/ fetuses/ babies | integer | 1 |  |
|  |  |  |  |  | OBX EpisodeHistory.TypeOfGestation | Type of gestation | coded_text | Singleton pregnancy |  |
|  |  |  |  |  | OBX Exam.@@Exam | Case ID | integer | 18158349\|18157436\|18157386\|18157336\|18157286 |  |
|  |  |  |  |  | OBX Exam.@@ExamType | Exam type | integer | 63\|60\|58 |  |
|  |  |  |  |  | OBX Exam.@@Patient | Patient ID | integer | 600697\|600647\|600597\|600547\|600497 |  |
|  |  |  |  |  | OBX Exam.@@VPDepartment | Department | integer | 2 |  |
|  |  |  |  |  | OBX Exam.@Id | Exam ID | integer | 18159164\|18158351\|18158350\|18157437\|18157387\|18157337\|18157287 |  |
|  |  |  |  |  | OBX Exam.CreatedAt | Created at | timestamp | 20250710155219\|20250710144937\|20250710135410\|20250710135358\|20250710135345\|20250710135333 |  |
|  |  |  |  |  | OBX Exam.ExamDate | Exam date | date | 20250923\|20250820\|20250710 |  |
|  |  |  |  |  | OBX Exam.ExamTime | Time | time | 154538\|144800\|144351\|135406\|135352\|135341\|135329 |  |
|  |  |  |  |  | OBX Exam.Export | Export | coded_text | N |  |
|  |  |  |  |  | OBX Exam.LangID | Language | integer | 1033 |  |
|  |  |  |  |  | OBX Exam.Role | Role | coded_text | E |  |
|  |  |  |  |  | OBX ExamAddData.AgeatExamDate | Age | integer | 24 |  |
|  |  |  |  |  | OBX ExamAddData.ExamState | Exam status | coded_text | Report finalized |  |
|  |  |  |  |  | OBX ExamAddData.ExamTitle | Exam subtype | coded_text | Fetal Echocardiogram\|Detailed Anatomy Assessment\|Detailed First Trimester Anatomy with Nuchal Translucency \|Fetal Echocardiogram with Detailed Anatomy Assessment \|Interval Fetal Growth\|Interval Fetal Growth  |  |
|  |  |  |  |  | OBX ExamAddData.Operator1 | Sonographer | coded_text | Aimee Heeze, RDMS |  |
|  |  |  |  |  | OBX ExamAddData.Operator3 | Reading physician | coded_text | Juliana Gevaerd Martins, M.D. |  |
|  |  |  |  |  | OBX ExamAddData.OperatorId3 | <OperatorId3.ShortLabel> | integer | 96 |  |
|  |  |  |  |  | OBX ExamContact.@@Contact_ref1 | <@@Contact_ref1.ShortLabel> | integer | 15894 |  |
|  |  |  |  |  | OBX ExamContact.@@Listitem | <@@Listitem.ShortLabel> | integer | 5545 |  |
|  |  |  |  |  | OBX ExamStateHistory.@Id | ID | integer | 52213858\|52213859\|56089357\|52212459\|52213857\|56089307\|52212457\|52212458\|56089207\|52210307\|... |  |
|  |  |  |  |  | OBX ExamStateHistory.Date | Date | date | 20250710\|20260410 |  |
|  |  |  |  |  | OBX ExamStateHistory.NewState | New state | coded_text | New exam\|Scan started\|Report finalized |  |
|  |  |  |  |  | OBX ExamStateHistory.StationName | Station name | coded_text | EVMC1LK5Q54\|JEDI1\|EVMCJKH4Q54 |  |
|  |  |  |  |  | OBX ExamStateHistory.Time | Time | time | 154538\|154808\|170739\|144800\|151706\|170725\|144351\|144604\|170712\|135406\|... |  |
|  |  |  |  |  | OBX ExamStateHistory.UserLoginName | User login name | coded_text | HeezeAL\|admin |  |
|  |  |  |  |  | OBX ImagingParameters.ExamConditions | View | coded_text | Adequate |  |
|  |  |  |  |  | OBX ImagingParameters.ImagingProcedure | Device/Procedure | coded_text | Voluson E22, Transabdominal ultrasound examination\|Voluson E22, Transabdominal and transvaginal ultrasound examination\|Voluson E22. Transabdominal ultrasound examination |  |
|  |  |  |  |  | OBX VP_MDT_SR_Files.Date | Date of MDT | date | 20250710\|20250717\|20260410 |  |
|  |  |  |  |  | OBX VP_MDT_SR_Files.Module | Module | coded_text | vpmain\|VPMain |  |
|  |  |  |  |  | OBX VP_MDT_SR_Files.UID | UID | coded_text | 1.2.276.0.26.1.1.1.2.2025.227.71280.5185292\|1.2.276.0.26.1.1.1.2.2025.227.69458.2785070\|1.2.276.0.26.1.1.1.2.2025.227.67594.4521521\|1.2.276.0.26.1.1.1.2.2025.227.67300.7632879\|1.2.276.0.26.1.1.1.2.2025.227.67054.4259429\|1.2.276.0.26.1.1.1.2.2025.227.66784.4374300\|1.2.276.0.26.1.1.1.2.2025.227.66530.7405429 |  |
|  |  |  |  |  | OBX WarningMessage |  | free_text | Exam contains manually modified mask texts, thus discrete values may be inaccurate. |  |
<!-- END: generated cluster=encounter -->

### non_fetal_gyn

Non-fetal gynecologic anatomy: adnexa, cervix, endomyometrial / uterine findings, uterine artery Doppler, gynecologic procedures.

_228 rows: 225 Observer, 4 HL7, 1 paired._

<!-- BEGIN: generated cluster=non_fetal_gyn -->
| concept_key | observer_path | observer_label_values | observer_value_class | observer_sample | viewpoint_path | viewpoint_short_label | viewpoint_value_class | viewpoint_sample | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | adnexa.left.done |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.ovry_loc |  | coded_text | Unspecified |  |  |  |  |  |
|  | adnexa.left.ovry_seen |  | coded_text | Unspecified |  |  |  |  |  |
|  | adnexa.left.ovry_size_a |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.ovry_size_b |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.ovry_size_c |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.ovry_surg_abs |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.ovry_vol |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.tube_hydrosalpinx |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.tube_hydrosalpinx_size_a |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.tube_hydrosalpinx_size_b |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.tube_hydrosalpinx_size_c |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.tube_hydrosalpinx_volume |  | integer | 0 |  |  |  |  |  |
|  | adnexa.left.tube_nrml |  | coded_text | Unspecified |  |  |  |  |  |
|  | adnexa.left.tube_seen |  | coded_text | Unspecified |  |  |  |  |  |
|  | adnexa.left.tube_surg_abs |  | integer | 0 |  |  |  |  |  |
|  | adnexa.masses |  | empty |  |  |  |  |  |  |
|  | adnexa.right.done |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.ovry_loc |  | coded_text | Unspecified |  |  |  |  |  |
|  | adnexa.right.ovry_seen |  | coded_text | Unspecified |  |  |  |  |  |
|  | adnexa.right.ovry_size_a |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.ovry_size_b |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.ovry_size_c |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.ovry_surg_abs |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.ovry_vol |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.tube_hydrosalpinx |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.tube_hydrosalpinx_size_a |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.tube_hydrosalpinx_size_b |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.tube_hydrosalpinx_size_c |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.tube_hydrosalpinx_volume |  | integer | 0 |  |  |  |  |  |
|  | adnexa.right.tube_nrml |  | coded_text | Unspecified |  |  |  |  |  |
|  | adnexa.right.tube_seen |  | coded_text | Unspecified |  |  |  |  |  |
|  | adnexa.right.tube_surg_abs |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_elective |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_emergency |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_ga_placement |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_lower_cx_post_tfp |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_lower_cx_standing |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_lower_cx_supine |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_mcdonald |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_shirodkar |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_upper_cx_post_tfp |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_upper_cx_standing |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cecrlage_upper_cx_supine |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cervicx_length_post_tfp |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cervicx_length_standing |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.cervicx_length_supine |  | decimal\|integer | 0\|3.5 |  |  |  |  |  |
|  | cervix.cervix.dilation |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.done |  | integer | 1\|0 |  |  |  |  |  |
|  | cervix.cervix.dynamic_chngs |  | coded_text | Unspecified |  |  |  |  |  |
|  | cervix.cervix.exam_performed_by_us |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.exam_performed_manually |  | integer | 0 |  |  |  |  |  |
| cervix.funneling | cervix.cervix.funneling |  | coded_text | Unspecified | OBX Cervix.FunnellingYN | Funneling | coded_text | Funneling absent |  |
|  | cervix.cervix.funneling_lngth_post_tfp |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.funneling_lngth_standing |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.funneling_lngth_supine |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.funneling_percent_post_tfp |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.funneling_percent_standing |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.funneling_percent_supine |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.funneling_width_post_tfp |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.funneling_width_standing |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.funneling_width_supine |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.int_os_to_ext_os_post_tfp |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.int_os_to_ext_os_standing |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.int_os_to_ext_os_supine |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.length |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix.normal |  | coded_text | Normal\|Unspecified |  |  |  |  |  |
|  | cervix.cervix.response_to_standing |  | coded_text | Unspecified |  |  |  |  |  |
|  | cervix.cervix.response_to_tfp |  | coded_text | Unspecified |  |  |  |  |  |
|  | cervix.cervix.response_to_tfp_debris |  | coded_text | Unspecified |  |  |  |  |  |
|  | cervix.cervix.response_to_valsalva |  | coded_text | Unspecified |  |  |  |  |  |
|  | cervix.cervix.surg_abs |  | integer | 0 |  |  |  |  |  |
|  | cervix.cervix_anomalies |  | empty |  |  |  |  |  |  |
|  | endomyocds.endo_contents |  | empty |  |  |  |  |  |  |
|  | endomyocds.gyn_anomalies |  | empty |  |  |  |  |  |  |
|  | endomyocds.gyn_data.cds_fld_amt |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.cds_fld_descr |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.cds_fld_other_txt |  | empty |  |  |  |  |  |  |
|  | endomyocds.gyn_data.cds_fld_seen |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.cds_fld_size_a |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.cds_fld_size_b |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.cds_fld_size_c |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.cds_fld_volume |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.done |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_colr_dop |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_cont_fld_pres |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_cont_fld_type |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_cont_other_txt |  | empty |  |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_dop_ri |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_dop_ri_value |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_lining |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_shape |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_thickness_cm |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.endo_thickness_layers |  | integer | 0 |  |  |  |  |  |
|  | endomyocds.gyn_data.gen_comment |  | empty |  |  |  |  |  |  |
|  | endomyocds.gyn_data.myo_homo_hetro |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.done |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.hysteroscopy_amt |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.hysteroscopy_done |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.hysteroscopy_fld_type |  | empty |  |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystgrpy_amt |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystgrpy_cath_type |  | coded_text | Unspecified |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystgrpy_cath_type_txt |  | empty |  |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystgrpy_done |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystgrpy_fld_type |  | coded_text | Unspecified |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystgrpy_fld_type_txt |  | empty |  |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystgrpy_nrml |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystsalgrpy_l_tube_fld_oth |  | empty |  |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystsalgrpy_lft_tube |  | coded_text | Unspecified |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystsalgrpy_lft_tube_blk |  | coded_text | Unspecified |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystsalgrpy_lft_tube_fld |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystsalgrpy_r_tube_fld_oth |  | empty |  |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystsalgrpy_rht_tube |  | coded_text | Unspecified |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystsalgrpy_rht_tube_blk |  | coded_text | Unspecified |  |  |  |  |  |
|  | gyn_procedure.gyn_procedure.sonohystsalgrpy_rht_tube_fld |  | integer | 0 |  |  |  |  |  |
|  | gyn_procedure.hormone_replacement_therapy |  | empty |  |  |  |  |  |  |
|  | uterine_artery.left.a_over_i |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.a_over_i_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.aedv |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.left.at |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.at_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.dominant |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.left.done |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.notch |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.left.notch_depth |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.pi |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.pi_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.psv |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.psv_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.rev_flow |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.left.ri |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.ri_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.sd |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.left.sd_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.a_over_i |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.a_over_i_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.aedv |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.postpartum_left.at |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.at_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.dominant |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.postpartum_left.done |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.notch |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.postpartum_left.notch_depth |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.pi |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.pi_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.psv |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.psv_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.rev_flow |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.postpartum_left.ri |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.ri_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.sd |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_left.sd_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.a_over_i |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.a_over_i_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.aedv |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.postpartum_right.at |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.at_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.dominant |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.postpartum_right.done |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.notch |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.postpartum_right.notch_depth |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.pi |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.pi_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.psv |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.psv_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.rev_flow |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.postpartum_right.ri |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.ri_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.sd |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.postpartum_right.sd_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.a_over_i |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.a_over_i_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.aedv |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.right.at |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.at_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.dominant |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.right.done |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.notch |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.right.notch_depth |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.pi |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.pi_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.psv |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.psv_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.rev_flow |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.right.ri |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.ri_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.sd |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.right.sd_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.a_over_i |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.a_over_i_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.aedv |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.subplacental.at |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.at_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.dominant |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.subplacental.done |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.notch |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.subplacental.notch_depth |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.pi |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.pi_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.psv |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.psv_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.rev_flow |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterine_artery.subplacental.ri |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.ri_pc |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.sd |  | integer | 0 |  |  |  |  |  |
|  | uterine_artery.subplacental.sd_pc |  | integer | 0 |  |  |  |  |  |
|  | uterus.bladder.contours |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterus.bladder.description |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterus.bladder.done |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.anteflexed |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.anteverted |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.dextroverted |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.done |  | integer | 1\|0 |  |  |  |  |  |
|  | uterus.uterus.levoverted |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.midplane |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.qual_size |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterus.uterus.retroflexed |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.retroverted |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.seen |  | coded_text | Visualized\|Unspecified |  |  |  |  |  |
|  | uterus.uterus.shape |  | coded_text | Unspecified |  |  |  |  |  |
|  | uterus.uterus.size_a |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.size_b |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.size_c |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus.surgically_absent |  | integer | 0 |  |  |  |  |  |
|  | uterus.uterus_anomalies |  | empty |  |  |  |  |  |  |
|  |  |  |  |  | OBX Cervix.Appearance | Cervix | coded_text | Visualized |  |
|  |  |  |  |  | OBX Cervix.ApproachCervicalBiometry | Approach | coded_text | Transvaginal with valsalva |  |
|  |  |  |  |  | OBX Cervix.OtherFindings | Cervix details | coded_text | normal |  |
<!-- END: generated cluster=non_fetal_gyn -->
