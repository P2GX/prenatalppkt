# Schema and pairing

Companion to [README.md](README.md). The clinician-facing field map lives there; this file documents the CSV column schema, value-class vocabulary, and the cluster-scoped pairing algorithm.

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
