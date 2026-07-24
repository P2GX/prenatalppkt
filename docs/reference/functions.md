# Functions and methods

This page lists the functions and methods most likely to matter during review.

## Observer extractor

Module:

```text
prenatalppkt.etl.extractors.observer
```

| Name | Kind | Meaning |
|---|---|---|
| `extract(data, factory=None)` | public function | Extracts the first fetus from Observer JSON |
| `extract_all_fetuses(data, factory=None)` | public function | Extracts every fetus and returns a dict by fetus number |
| `extract_from_file(filepath, factory=None)` | public function | Loads JSON from a file and calls `extract()` |
| `extract_all_fetuses_from_file(filepath, factory=None)` | public function | Loads JSON and calls `extract_all_fetuses()` |
| `_validate_structure(data)` | helper | Checks the input has a non-empty `fetuses` list |
| `_validate_fetus_count(fetuses, declared_count)` | helper | Warns if declared fetus count disagrees with the array |
| `_extract_one_fetus(fetus_data, factory)` | helper | Extracts one fetus after scan-type classification |
| `_parse_measurements(fetus_data, fetus_number, factory)` | helper | Parses T2/T3 measurements |
| `_parse_single_measurement(m, fetus_number, factory)` | helper | Parses one measurement |
| `_parse_t1_measurements(fetus_data, fetus_number, factory)` | helper | Parses CRL/NT first-trimester measurements |
| `_convert_to_mm(value, unit)` | helper | Converts cm or mm to millimeters |

## Scan type

Module:

```text
prenatalppkt.etl.scan_type
```

| Name | Kind | Meaning |
|---|---|---|
| `ScanType` | enum | `FIRST_TRIMESTER`, `T2_T3_BIOMETRY`, or `UNKNOWN` |
| `UnsupportedScanTypeError` | error class | Raised for unsupported scan shapes |
| `classify_fetus(fetus_data)` | function | Classifies one fetus by measurement labels |
| `detect_scan_type(observer_json)` | function | Classifies the first fetus in an Observer JSON file |

## Section parsers

Package:

```text
prenatalppkt.etl.sections
```

| Name | Meaning |
|---|---|
| `parse_clinical_indication(data, source_format)` | Reason for exam |
| `parse_pregnancy_dating(data, source_format)` | LMP, EDD, gestational age |
| `parse_clinical_impression(data, source_format, hpo_cr=None)` | Impression text and optional HPO terms |
| `parse_fetal_anatomy(data, source_format, hpo_cr=None, fetus_index=0, fetus_number=1)` | Anatomy structures, anomalies, and optional HPO terms - `fetus_index`/`fetus_number` select which fetus's own data to read (Observer/ViewPoint HL7 respectively) in a multi-fetus exam |
| `parse_estimated_fetal_weight(data, source_format)` | EFW grams, percentile, method, growth category |
| `parse_fetal_ratios(data, source_format)` | Ratio values and proportionality assessment |
| `parse_maternal_history(data, source_format="viewpoint_text")` | Maternal history placeholder |
| `parse_placenta(data, source_format="viewpoint_text")` | Placenta placeholder |
| `parse_amniotic_fluid(data, source_format="viewpoint_text")` | Amniotic fluid placeholder |
| `parse_umbilical_cord(data, source_format="viewpoint_text")` | Umbilical cord placeholder |

## Mapping functions

| Name | Module | Meaning |
|---|---|---|
| `BiometryMappingLoader.load(path)` | `prenatalppkt.mapping_loader` | Reads YAML mapping rules |
| `TermBinFactory.create_term_bin(...)` | `prenatalppkt.etl.term_bin_factory` | Creates one mapped `TermBin` |
| `validate_required_measurements(term_bins)` | `prenatalppkt.etl.term_bin_factory` | Checks HC, BPD, AC, and Femur are present |
| `normalize_measurement_name(raw_name, format_map=None)` | `prenatalppkt.etl.constants` | Maps raw labels to canonical names |
| `is_target_measurement(raw_name, format_map=None)` | `prenatalppkt.etl.constants` | Checks if a raw label is recognized |

## Reference lookup

Module:

```text
prenatalppkt.biometry_reference
```

| Name | Kind | Meaning |
|---|---|---|
| `FetalGrowthPercentiles(source="intergrowth")` | class | Loads reference tables |
| `lookup_percentile(measurement_type, gestational_age_weeks, value_mm)` | method | Finds percentile for a measurement |
| `lookup_zscore(measurement_type, gestational_age_weeks, value_mm)` | method | Finds z-score if the source has z-score data |

## HPO

| Name | Module | Meaning |
|---|---|---|
| `HpoParser(...)` | `prenatalppkt.hpo.hpo_parser` | Loads HPO |
| `get_ontology()` | `HpoParser` | Returns the HPO ontology object |
| `get_id_to_label_map()` | `HpoParser` | Builds HPO id to label map |
| `get_hpo_concept_recognizer()` | `HpoParser` | Returns text-to-HPO recognizer |
| `get_version()` | `HpoParser` | Returns HPO version |
| `HpoConceptRecognizer.parse(text)` | `prenatalppkt.hpo.hpo_cr` | Abstract base class - `parse()` is the extension point for any text-to-HPO backend |
| `FenominalConceptRecognizer.parse(text)` | `prenatalppkt.hpo.fenominal_cr` | The one concrete implementation - fenominal text matching with negation |

## Genomics scaffold

| Name | Module | Meaning |
|---|---|---|
| `scan_vcf_text(text, genome_assembly="unknown")` | `prenatalppkt.genomics.vcf` | Scans VCF text |
| `scan_vcf_file(path, genome_assembly="unknown")` | `prenatalppkt.genomics.vcf` | Scans a VCF file |
| `scan_vcf_archive(path, genome_assembly="unknown")` | `prenatalppkt.genomics.vcf` | Scans VCF files in an archive |
| `to_vcf_record(variant)` | `prenatalppkt.genomics.genomic` | Builds Phenopacket VCF record |
| `to_variation_descriptor(variant)` | `prenatalppkt.genomics.genomic` | Builds variation descriptor |
| `build_vcf_file_entry(uri, attributes=None)` | `prenatalppkt.genomics.genomic` | Builds Phenopacket file entry |
| `build_genomic_interpretation(variants, subject_id, interpretation_id)` | `prenatalppkt.genomics.genomic` | Builds inert genomic interpretation scaffold |

