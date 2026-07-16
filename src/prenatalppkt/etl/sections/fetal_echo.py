"""
Fetal echocardiography section parser (SKELETON).

Real cardiac data exists in both Observer JSON and ViewPoint HL7, but
nothing parses it yet. The field names below were found in the data
dictionary (scripts/data_dict/), not guessed.

TODO @VarenyaJ: Complete implementation - map cardiac structure states to
HPO terms and decide whether the embedded numeric echo measurements
(aortic root diameter, ventricle dimensions, valve Zscore diameters) get
parsed here or handled separately, since those need new
BiometryMeasurement enum members and growth-reference curves - the same
clinical-authority gap as the SGA/LGA growth classification.
"""

from typing import Dict


def parse_fetal_echo(data, source_format: str, hpo_cr=None) -> Dict:
    """
    Parse fetal echocardiography section.

    Args:
        data: Raw input data (JSON string, dict, or text)
        source_format: One of "observer_json", "viewpoint_text", "viewpoint_hl7"
        hpo_cr: Optional concept recognizer for HPO term extraction from
                free-text findings.

    Returns:
        Dict with keys:
            - normal_structures: List[str] - Cardiac structures marked Normal
            - abnormal_structures: List[str] - Cardiac structures marked Abnormal
            - not_visualized: List[str] - Cardiac structures marked Unseen
            - findings: List[Dict] - Specific cardiac findings (structure + description)
            - hpo_terms: List[SimpleTerm] - HPO terms extracted from findings
            - source_format: str

    TODO @VarenyaJ Implementation steps:
        1. Observer JSON: fetuses[].fetal_echo_anatomy[] uses the exact
           same main.label / main.anat_state / detail[] / anomalies[]
           shape as fetuses[].fetus.anatomy[] (the regular anatomy
           parser) - reuse _process_anatomy_item / _classify_structure
           from fetal_anatomy.py rather than rewriting that logic.
        2. ViewPoint HL7: HeartFetus.HeartAppearance and
           HeartFetus.VisceroAtrialSitusAppearance are the top-level
           state fields (normal/abnormal/suboptimal - same 3-value
           vocabulary as the regular anatomy fields). About 11 *Details
           free-text fields (AortaAscDetails, AorticIsthmusDetails,
           AtriaDetails, AtrioVentricularConnectionsDetails,
           GreatArteryCrossingDetails, HeartDetails,
           PulmonaryArtery{L,Main,R}Details,
           VenousAtrialConnectionsDetails,
           VentricleArteryConnectionsDetails, VentriclesDetails) feed
           HPO extraction the same way the regular anatomy Details
           fields do.
        3. Cardiac also has several coded findings with no equivalent in
           the regular anatomy parser: CardiacRhythm, CardiacFunction,
           CardiacPosition, CardiacProportions, CardiacSize,
           PericardialEffusion, IntracardiacEchogenicFocusPrint - each
           needs its own HPO-mapping design, not just a
           Normal/Abnormal/Unseen classification.
        4. Numeric echo measurements (Observer's fetuses[].dm_echo.* -
           aortic root diameter, biventricular dimensions,
           interventricular septum, left/right ventricle; ViewPoint's
           roughly 40 valve annulus diameter + Zscore fields) are a
           separate, larger decision - not attempted here.
    """
    return {
        "normal_structures": [],
        "abnormal_structures": [],
        "not_visualized": [],
        "findings": [],
        "hpo_terms": [],
        "source_format": source_format,
    }
