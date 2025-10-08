# Sonographic Measurements
==========================

This document describes the new class-based architecture for evaluating fetal sonographic measurements against validated growth  references (NIHCD and INTERGROWTH-21st). It focuses on clear separation between **numerical evaluation** and **ontology mapping**.

-----------------------------------------------------------------------------------------------------------------------------------------------------
1. Overview
-----------------------------------------------------------------------------------------------------------------------------------------------------

Flow of computation:

            Measurement Value (mm)
                    |
                    v
        +---------------------------+
        |      ReferenceRange       |
        | - Applies percentile bins |
        +---------------------------+
                    |
                    v
        +---------------------------+
        |   MeasurementResult       |
        | - Encodes percentile bin  |
        +---------------------------+
                    |
                    v
        +---------------------------+
        |   SonographicMeasurement  |
        | - Abstract base evaluator |
        +---------------------------+
                    |
                    v
        +---------------------------+
        |   TermObservation         |
        | - Ontology layer |
        +---------------------------+

Each layer is modular and testable, making it easy to extend for new measurements such as HC, BPD, AC, FL, OFD, and EFW.

-----------------------------------------------------------------------------------------------------------------------------------------------------
2. Core Files
-----------------------------------------------------------------------------------------------------------------------------------------------------

|---------------------------------------------------------------------------------------------------------------------------------------------------|
| File                              |                                                   Purpose                                                     |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------|
| **gestational_age.py**            | Represents gestational age in weeks and days. Provides `from_weeks()` and human-readable formatting.          |
| **percentile.py**                 | Defines key percentile thresholds (3rd-97th). Used across all tables.                                         |
| **measurement_result.py**         | Encapsulates which percentile interval a value belongs to (e.g. below 3rd, 5th-10th).                         |
| **reference_range.py**            | Compares a numeric measurement to percentile cutoffs for a given gestational age.                             |
| **sonographic_measurement.py**    | Abstract base class. Provides standard `evaluate()` method and hooks for subclasses.                          |
| **bpd_measurement.py**            | Implements the biparietal diameter measurement. Uses NIHCD reference thresholds.                              |
| **femur_length_measurement.py**   | Implements the femur length measurement. Demonstrates lower-only ontology mapping.                            |
| **term_observation.py**           | Wraps measurement results with ontology metadata (HPO term, observed/excluded flag).                          |
|---------------------------------------------------------------------------------------------------------------------------------------------------|

-----------------------------------------------------------------------------------------------------------------------------------------------------
3. Example Usage
-----------------------------------------------------------------------------------------------------------------------------------------------------

```python
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.bpd_measurement import BiparietalDiameterMeasurement

# Example thresholds from NIHCD for 20.86 weeks
ga = GestationalAge.from_weeks(20.86)
thresholds = [145.25, 147.25, 150.37, 161.95, 174.41, 178.12, 180.56]
reference = ReferenceRange(gestational_age=ga, percentiles=thresholds)

# Evaluate a measurement (in mm)
bpd = BiparietalDiameterMeasurement()
observation = bpd.evaluate(
    gestational_age=ga,
    measurement_value=170.0,
    reference_range=reference
)

print(observation)
# Output:
# TermObservation(hpo_label='None', observed=False, excluded=True, gestational_age=20w6d)