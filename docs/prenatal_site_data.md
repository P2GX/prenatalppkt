# prenatal-site-data corpus reference

Background reading for anyone (human or agent) about to parse, lint,
or transform the prenatal data flowing through this library.
Describes the two source corpora that live under the sibling
`prenatal-site-data/` directory (gitignored relative to this repo;
maintained as a separate clone / private mirror).

## Layout

```
PreGen/
|- prenatalppkt/        (this repo)
|- prenatal-site-data/  (sibling; not in git)
   |- observer/center/CUIMC/pretty_print/
   |  |- Apple_Sally.json          (raw export)
   |  |- Apple_Sally_pretty.json   (pretty-printed; used for parsing)
   |  |- Blue_Sally.json
   |  |- Blue_Sally_pretty.json
   |  |- ... (5 patients total, raw + pretty pair each)
   |
   `- viewpoint/center/evms/GE_export_of_EVMS_test_cases/
      |- phenotype_1.txt
      |- phenotype_2.txt
      |- ... (7 phenotype files total)
```

All patient identifiers in the corpus are fictional (Sally Apple,
Sally Blue, Sally Charm, Sally Diva, Sally Eclair; HL7 Phenotype
Test 1-7). Safe to reference in code hosts and public artifacts.
Refresh the sibling dir from the upstream private mirror when new
site exports arrive.

## CUIMC Observer JSON

Five `*_pretty.json` files, ~1,700 lines each. Each file is one
exam encounter for one patient, exported from the Observer system
at CUIMC. The pretty-printed variant is the canonical parsing
target; the raw `.json` siblings are byte-equivalent without the
indentation.

### Top-level structure

Ten top-level keys per file:

| Key | Shape | Notes |
|---|---|---|
| `exam` | dict | Encounter metadata: site, patient demographics, ICD-10 indications, referring providers, gestational age fields. |
| `adnexa` | dict | Left + right ovary + tube observations. Almost always Unspecified in fetal scans. |
| `cervix` | dict | Cervix measurements. |
| `endomyocds` | dict | Endometrium / myometrium observations. |
| `finalize` | dict | Sign-off metadata. |
| `gyn_procedure` | dict | GYN procedure metadata. |
| `hist_phys_vitals` | dict | Patient vitals (BP, weight). |
| `uterine_artery` | dict | Doppler observations. |
| `uterus` | dict | Uterus measurements. |
| `fetuses` | list | One element per fetus. The dense load-bearing namespace. |

### `fetuses[]` element shape

Each element is one fetus per encounter. Twenty sub-keys; the
load-bearing ones for downstream ETL:

| Sub-key | Shape | Notes |
|---|---|---|
| `fetus` | dict | Per-fetus metadata: gender, GA-by-sonography, heart rate, presentation, impression text. |
| `measurements` | list[dict] | Biometry. One dict per measurement. See "Measurement element" below. |
| `anatomy` | list[dict] | Anatomy tree. Region groups with main/detail/anomalies sub-arrays. |
| `ratios` | list[dict] | Cross-measurement ratios (HC/AC, FL/AC, FL/BPD). |
| `efws` | list[dict] | Estimated fetal weights (one per formula: AC+FL+HC, AC+FL, AC+BPD). |
| `amioticfluid` | dict | Amniotic fluid volume. Legacy typo (missing `n` in "amioticfluid"); preserved verbatim from the Observer schema. |
| `firsttrimester` | dict | First-trimester only fields (CRL, NT). |
| `impression` | dict | Per-fetus impression text. |
| `fetal_echo_anatomy` | dict | Fetal echo specifics. |
| `fetal_echo_measurements` | dict | Fetal echo measurements. |
| `fetalvessels` | dict | Cord / vessel observations. |
| `nst`, `bpp`, `dm_echo`, `ectopic_preg`, `fbscvs`, `otherprocs`, `placenta`, `uards` | dict | Less common observation types. |

### Measurement element

Each `fetuses[].measurements[]` entry has this shape:

```
{
  "label": "AC",                          // qualitative label
  "value": 22.62,                         // numeric measurement
  "decimal_places": 2,                    // display precision
  "unit_of_measure": "cm",                // measurement unit
  "calculated_ega": 26.9,                 // EGA from this measurement (decimal weeks)
  "calculated_percentile": 55.6,          // percentile as float
  "percentile_for_display": "56%",        // percentile as `%`-suffixed string
  "include_in_avg_ga_calc": 1,            // 1/0 flag
  "print_in_report": 1,                   // 1/0 flag
  "calculated_z_score": 0,                // z-score
  "fetus_number": 1                       // which fetus this row belongs to
}
```

Labels observed in this corpus: `AC`, `BPD`, `Cerebellum`, `Femur`,
`HC`, `Nuchal Fold`, `CRL`, `Humerus`. Same shape applies to
`ratios[]` (label = `HC/AC`, `FL/AC`, `FL/BPD`) and `efws[]`
(label = `EFW (AC, FL, HC)` etc.).

### Value-type tokens emitted by the parser

The walker classifies each leaf into one of: `int`, `float`,
`bool`, `null`, `str`, `list`, `dict`, `percentile_str`
(`^-?\d+(\.\d+)?%$` or `^[<>]\d+%$`), `weeks_days_str`
(`^\d+w \d+d$`).

## EVMS GE HL7 v2.4

Seven `phenotype_*.txt` files, 95-250 lines each, totalling ~1,374
OBX rows. Each file is one exam, exported from a GE ViewPoint
system at EVMS in HL7 v2.4 pipe-delimited form.

### Segment summary

| Segment | Role | Parser coverage |
|---|---|---|
| `MSH` | Message header (sender, encoding) | Read once for sanity; never observation data. |
| `PID` | Patient demographics (name, sex, DOB) | NOT in OBX; skipped by the current data-dict parser. |
| `ZED` | Custom GE extension (exam IDs, signing) | Skipped. |
| `OBR` | Order header | Skipped. |
| `OBX` | Observation (the only data segment) | This is where every measurement, anatomy finding, and free-text impression lives. |

### OBX field semantics

Each OBX line splits on `|` into:

| Position | Meaning | Example |
|---|---|---|
| `OBX-1` | Sequence index | `4` |
| `OBX-2` | Declared HL7 type | `NM` (numeric), `ST` (string), `DT` (date), `TM` (time), `TS` (timestamp) |
| `OBX-3` | Identifier triple `Namespace.Field^ShortLabel^LongLabel` | `SkullFetus.HeadCircumference^HC^Head circumference` |
| `OBX-4` | Sub-id (per-fetus) | `Fetus1` or empty |
| `OBX-5` | Value | `225.2^225.2` (NM) or `cloverleaf shape` (ST) |

The first `^`-segment of OBX-3 is the primary identifier
(`SkullFetus.HeadCircumference`); short label and long label live
in the remaining segments and are typically discarded.

### Type distribution in this corpus

| OBX-2 type | Count | Example |
|---|---|---|
| `ST` | 723 | Free-text strings, qualitative labels (`normal`, `abnormal`). |
| `NM` | 548 | Numeric measurements. Values stored as `^`-doubled strings (`225.2^225.2`); split on `^` and take the first segment. |
| `DT` | 68 | Date. |
| `TM` | 28 | Time. |
| `TS` | 7 | Timestamp. |

### Namespace prefixes observed

`AbdomenFetus`, `AntenatalBookingHistory`, `BabyPatientData`,
`BrainFetus`, `Cervix`, `ChestFetus`, `Coding`, `CodingDiagnosis`,
`CodingProcedure`, `EmbryonicStructuresFetus`, `EpisodeHistory`,
`Exam`, `ExamAddData`, `ExamCodingIndication`, `ExamContact`,
`ExamOBDating`, `ExamStateHistory`, `ExtremitiesFetus`, `FaceFetus`,
`FetalEchocardiography`, `Fetus`, `GastrointestinalTractFetus`,
`HeartFetus`, `ImagingParameters`, `MaternalScreeningTests`,
`NeckSkinFetus`, `PatientAnamnesticData`, `PatientFamilyHistory`,
`PatientHistory`, `SkullFetus` (+ a handful more).

The `<BodyPart>Fetus` pattern is the anatomy-region grouping; the
non-suffixed names (`Exam`, `PatientHistory`, etc.) carry
encounter / demographic data.

## Cross-corpus quirks worth remembering

- **Numeric percentiles**: Observer stores percentile both as a
  float (`calculated_percentile = 55.6`) and as a `%`-suffixed
  string (`percentile_for_display = "56%"`). HL7 stores the same
  percentile as an NM value in a dedicated identifier
  (`<Region>Fetus.VP_<Measurement>_Percentile`), `^`-doubled.
- **Units**: Observer biometry is in cm (with `unit_of_measure`
  field). HL7 biometry is in mm. Plan 07 standardizes on LOINC
  codes downstream.
- **Free text**: Observer free-text impressions live at
  `fetuses[].fetus.impression_text` etc. HL7 stores them as
  multi-line ST values in `ExamAddData.ExamImpression`,
  `RequestedProcedure.RelevantClinicalInfo` etc., with
  embedded `\.br\` line-break escapes.
- **First-trimester scans**: only CRL / NT measurements are
  populated; AC / BPD / HC / Femur are absent.
- **Patient ID alignment**: Observer uses
  `exam.patient.first_name + last_name + b_date`; HL7 uses
  `PID-3` (subject ID) and OBX `Exam.@@Patient` (numeric patient
  ID). The two are not yet wired together.
- **Legacy typo**: Observer keys the amniotic-fluid sub-dict as
  `amioticfluid` (no `n`). The Observer schema does the same;
  preserved verbatim.
