# Building blocks

The codebase is easiest to understand as a set of small building blocks. Each
block owns one idea.

## Gestational age

Module:

```text
prenatalppkt.gestational_age
```

Class:

```text
GestationalAge
```

Methods and properties:

| Name | Kind | Meaning |
|---|---|---|
| `GestationalAge(weeks, days)` | constructor | Make a gestational age object |
| `GestationalAge.from_weeks(weeks)` | static method | Convert decimal weeks to weeks and days |
| `weeks` | property | Completed weeks |
| `days` | property | Additional days |

Plain meaning:

> Gestational age is timing context. A fetal measurement only has clinical
> meaning if we know how far along the pregnancy is.

## HPO terms

Module:

```text
prenatalppkt.hpo.simple_term
```

Class:

```text
SimpleTerm
```

Fields and properties:

| Name | Kind | Meaning |
|---|---|---|
| `hpo_id` | property | HPO identifier, such as `HP:0000252` |
| `hpo_label` | property | Human-readable HPO label |
| `excluded` | property | Whether the term is explicitly not observed |
| `gestational_age` | property | Optional timing context |

Plain meaning:

> `SimpleTerm` is a small HPO result object. It is used when the code needs an
> HPO id, label, and excluded flag without carrying the whole ontology object.

## Percentile ranges

Module:

```text
prenatalppkt.measurements.percentile_range
```

Class:

```text
PercentileRange
```

Methods and properties:

| Name | Kind | Meaning |
|---|---|---|
| `contains(perc)` | method | Checks if a percentile belongs in the range |
| `evaluate(perc)` | static method | Converts a percentile number to a standard range |
| `from_min_max(min, max)` | static method | Builds a range from YAML bounds |
| `bin_key` | property | Text label for the range |

Plain meaning:

> `PercentileRange` is a bucket for a percentile number.

## HPO-mapped measurement bins

Module:

```text
prenatalppkt.measurements.term_bin
```

Class:

```text
TermBin
```

Fields and methods:

| Name | Kind | Meaning |
|---|---|---|
| `range` | field | Percentile range |
| `hpo_id` | field | HPO identifier |
| `hpo_label` | field | HPO label |
| `normal` | field | Whether this bin represents normal range |
| `description` | field | Human-readable measurement summary |
| `loinc_code` | field | LOINC assay id for the raw measurement |
| `value_mm` | field | Raw value in millimeters |
| `gestational_age_weeks` | field | Gestational age as decimal weeks |
| `fits(percentile)` | method | Checks if this bin applies |
| `category` | property | Coarse bin category |
| `to_measurement_dict()` | method | Builds a Phenopacket-style raw measurement dict |

Plain meaning:

> `TermBin` connects a percentile range to an HPO term and raw measurement
> metadata.

## Measurement observations

Module:

```text
prenatalppkt.term_observation
```

Class:

```text
TermObservation
```

Fields and methods:

| Name | Kind | Meaning |
|---|---|---|
| `hpo_id` | field | HPO identifier |
| `hpo_label` | field | HPO label |
| `category` | field | Bin category |
| `observed` | field | Whether the abnormal finding is present |
| `gestational_age` | field | Timing context |
| `percentile` | field | Original percentile |
| `to_phenotypic_feature()` | method | Converts to Phenopacket-style feature dict |

Plain meaning:

> `TermObservation` is the older interpreted-measurement result object.

## Shared builder helpers

Module:

```text
prenatalppkt.builders._shared
```

The Observer and ViewPoint builders build one Phenopacket per fetus from a
term-bin list plus narrative HPO terms, so this logic is identical between
them and lives in one place instead of two:

| Name | Meaning |
|---|---|
| `parse_ga_from_description(description)` | Finds gestational age in a `TermBin` description |
| `resolve_subject_ga(dating, term_bins)` | Chooses the subject gestational age |
| `biometry_feature(tb)` | Converts one `TermBin` to a Phenopacket feature |
| `narrative_feature(term, description_prefix, subject_ga)` | Converts one narrative HPO term to a feature |
| `dedup_by_hpo_id(features)` | Removes duplicate HPO ids |
| `hpo_resource(hpo_parser)` | Builds HPO metadata (also reused by the gyn builder) |
| `phenopacket_id(accession_id, fetus_number)` | Builds the Phenopacket id |
| `subject_id(accession_id, fetus_number)` | Builds the subject id |

## Observer Phenopacket builder

Module:

```text
prenatalppkt.builders.observer_phenopacket
```

Public function:

| Name | Kind | Meaning |
|---|---|---|
| `build_observer_phenopacket(data, hpo_parser, created_at, accession_id=None)` | function | Builds one Phenopacket per fetus from Observer JSON |

This module imports its GA-resolution, feature-construction, dedup, and
id-formatting logic from `builders._shared` above rather than defining its
own copies.

Plain meaning:

> The builder is the main assembly point. It turns parsed data into the final
> GA4GH object. Each fetus in a twin/multi-fetus exam gets its own anatomy
> findings - the anatomy section parser is called once per fetus, keyed by
> that fetus's own list position, not once for the whole exam.

