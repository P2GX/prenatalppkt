"""
Section parsers for non-biometry clinical data.

These parsers extract additional clinical information from ultrasound reports
beyond fetal biometry measurements. They are designed to eventually integrate
with HPO Clinical Record (CR) modules for comprehensive phenotype capture.

Current Status: SKELETON IMPLEMENTATIONS
- Basic parsing structure in place
- Returns placeholder data
- TODO comments describe future implementation

Future Integration:
- Map findings to HPO terms using src/prenatalppkt/hpo modules
- Support symmetric processing across Observer JSON, ViewPoint Text, and HL7
- Enable full phenotype packet generation
"""

from prenatalppkt.etl.sections.maternal_history import parse_maternal_history
from prenatalppkt.etl.sections.clinical_impression import parse_clinical_impression
from prenatalppkt.etl.sections.clinical_indication import parse_clinical_indication
from prenatalppkt.etl.sections.pregnancy_dating import parse_pregnancy_dating
from prenatalppkt.etl.sections.fetal_anatomy import parse_fetal_anatomy
from prenatalppkt.etl.sections.placenta import parse_placenta
from prenatalppkt.etl.sections.amniotic_fluid import parse_amniotic_fluid
from prenatalppkt.etl.sections.umbilical_cord import parse_umbilical_cord

__all__ = [
    "parse_maternal_history",
    "parse_clinical_impression",
    "parse_clinical_indication",
    "parse_pregnancy_dating",
    "parse_fetal_anatomy",
    "parse_placenta",
    "parse_amniotic_fluid",
    "parse_umbilical_cord",
]
