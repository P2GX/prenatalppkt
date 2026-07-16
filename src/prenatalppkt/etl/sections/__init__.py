"""
Section parsers for non-biometry clinical data.

These parsers extract additional clinical information from ultrasound reports
beyond fetal biometry measurements. They return Dict objects with parsed data.

Implemented parsers:
- parse_clinical_indication: Extract reason for exam
- parse_pregnancy_dating: Extract LMP, EDD, gestational age
- parse_clinical_impression: Extract clinical narrative and HPO terms
- parse_fetal_anatomy: Extract anatomy findings and HPO terms
- parse_estimated_fetal_weight: Extract EFW and growth classification
- parse_fetal_ratios: Extract biometric ratios and proportionality

Skeleton parsers (TODO):
- parse_maternal_history: OB history, complications
- parse_placenta: Placental assessment
- parse_amniotic_fluid: AFI, MVP measurements
- parse_umbilical_cord: Vessel count, insertion site
- parse_fetal_echo: Cardiac structure findings and measurements
"""

from prenatalppkt.etl.sections.maternal_history import parse_maternal_history
from prenatalppkt.etl.sections.clinical_impression import parse_clinical_impression
from prenatalppkt.etl.sections.clinical_indication import parse_clinical_indication
from prenatalppkt.etl.sections.pregnancy_dating import parse_pregnancy_dating
from prenatalppkt.etl.sections.fetal_anatomy import parse_fetal_anatomy
from prenatalppkt.etl.sections.estimated_fetal_weight import (
    parse_estimated_fetal_weight,
)
from prenatalppkt.etl.sections.fetal_ratios import parse_fetal_ratios
from prenatalppkt.etl.sections.placenta import parse_placenta
from prenatalppkt.etl.sections.amniotic_fluid import parse_amniotic_fluid
from prenatalppkt.etl.sections.umbilical_cord import parse_umbilical_cord
from prenatalppkt.etl.sections.fetal_echo import parse_fetal_echo

__all__ = [
    "parse_maternal_history",
    "parse_clinical_impression",
    "parse_clinical_indication",
    "parse_pregnancy_dating",
    "parse_fetal_anatomy",
    "parse_estimated_fetal_weight",
    "parse_fetal_ratios",
    "parse_placenta",
    "parse_amniotic_fluid",
    "parse_umbilical_cord",
    "parse_fetal_echo",
]
