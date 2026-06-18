"""Per-cluster prose + value-class labels + table column order."""

from __future__ import annotations

VALUE_CLASS_LABEL: dict[str, str] = {
    "decimal": "number",
    "integer": "number",
    "percentile": "percentile",
    "coded_text": "coded",
    "free_text": "free text",
    "weeks_days": "weeks+days",
    "date": "date",
    "time": "time",
    "timestamp": "timestamp",
    "boolean": "yes/no",
    "empty": "",
}


CLUSTER_TEMPLATE_GUIDANCE: dict[str, str] = {
    "biometry": (
        "Both systems capture the core biometry suite (BPD, AC, HC, CRL, "
        "Femur, Humerus, Nuchal Fold) as numbers in mm. ViewPoint reports "
        "one HL7 field per measurement; Observer stores them as a list "
        "tagged by `label`. The XLSX should have one row per measurement "
        "with a number column for the raw value and a percentile column."
    ),
    "anatomy_brain": (
        "ViewPoint has a discrete `BrainFetus.*` HL7 namespace (ventricles, "
        "cerebellum, choroid plexus, posterior fossa). Observer captures the "
        "same findings inside free-text `fetuses[].anatomy[].*.brain` fields. "
        "The XLSX should pre-define brain anatomy fields so the receiving "
        "center isn't forced to free-type them."
    ),
    "anatomy_face_neck": (
        "ViewPoint has `FaceFetus.*`; Observer keeps these as free-text "
        "anatomy entries. Pre-define orbits, lips, palate, profile, neck "
        "fields in the XLSX."
    ),
    "anatomy_chest_gi": (
        "ViewPoint splits chest (non-cardiac) and GI into discrete fields; "
        "Observer lumps them into anatomy free text. Pre-define discrete "
        "chest + GI anatomy fields in the XLSX."
    ),
    "anatomy_spine": (
        "ViewPoint has `SpineFetus.*`; Observer keeps spine findings under "
        "free-text anatomy. The XLSX should pre-define spine fields."
    ),
    "anatomy_urinary": (
        "ViewPoint has `UrinaryTractFetus.*` (kidneys, bladder, ureters); "
        "Observer mostly free-text. Pre-define the urinary fields in the XLSX."
    ),
    "anatomy_general": (
        "Observer-only structural anatomy wrappers. ViewPoint has no "
        "equivalent namespace. The XLSX should provide a wide free-text "
        "column for system-agnostic anatomy notes."
    ),
    "cardiac": (
        "Both systems carry detailed cardiac findings and echocardiography "
        "measurements. The XLSX should accommodate both discrete "
        "cardiac-anatomy fields and free-text echocardiography findings."
    ),
    "amniotic_fluid": (
        "Both systems carry amniotic-fluid index and deepest-pocket. "
        "Numbers in cm. The XLSX should have AFI and SDP numeric columns "
        "plus a categorical (oligo / normal / polyhydramnios)."
    ),
    "placenta_cord": (
        "Both systems cover placenta + cord findings but tokenize "
        "differently (Observer's `cord.numberOfVessels` vs ViewPoint's "
        "`Cord.VesselCount`). The XLSX should include both naming styles "
        "as alias columns until a concept alias is hand-curated."
    ),
    "fetal_procedures": (
        "Observer-only invasive procedures (amniocentesis, CVS/FBS, "
        "ectopic mgmt). The XLSX should provide a procedure-type column "
        "plus a free-text findings column."
    ),
    "fetus_core": (
        "Both systems carry per-fetus identity (fetal sex, presentation, "
        "movements, tone). Fetal sex maps directly to a coded enum. The "
        "XLSX should have one row per fetus with these as columns."
    ),
    "indication_impression": (
        "Both systems carry ICD-10 indication codes + descriptions. Coded "
        "in both. The XLSX should have an indication-code column "
        "(ICD-10 format) and a free-text impression column."
    ),
    "dating": (
        "Both systems carry pregnancy dating: LMP, EDD, gestational age, "
        "agreed dating string. They tokenize differently (Observer's "
        "`ga_by_dates` vs ViewPoint's `ExamOBDating.*`). The XLSX should "
        "have LMP, EDD, GA-at-exam, and dating-method columns."
    ),
    "encounter": (
        "Exam-level metadata: date, location, signing, exam type, referring "
        "provider, accession. ViewPoint has structured `Exam.*` + "
        "`ExamAddData.*`; Observer scatters this under `exam.*` keys. The "
        "XLSX should pre-define encounter metadata as a header block."
    ),
    "maternal_subject": (
        "Both systems carry maternal demographics + obstetric history "
        "(gravida, para, name, age). Coded in both. The XLSX should have a "
        "maternal header block with these as standard columns."
    ),
    "non_fetal_gyn": (
        "Mostly Observer-only gynecologic findings (adnexa, cervix, "
        "uterine artery, gyn procedures). Cervix funneling is the one "
        "concept paired across sources. The XLSX should provide a "
        "free-text gyn-findings block plus discrete cervix-length / "
        "funneling columns."
    ),
    "_unclustered": (
        "Should stay empty. If a row lands here, clusters.yaml needs a new prefix."
    ),
}


CLUSTER_NOTES: dict[str, str] = {
    "biometry": (
        "Fetal biometric measurements (HC, BPD, AC, FL, etc.), growth "
        "ratios, EFW values, first-trimester measurements (CRL, NT), "
        "and the GE FGR data block. Observer rows split by measurement "
        "label so each (BPD, AC, HC, ...) gets its own row."
    ),
    "anatomy_brain": "Fetal brain anatomy: ventricles, cerebellum, choroid plexus, posterior fossa.",
    "anatomy_face_neck": "Fetal face and neck anatomy: orbits, lips, palate, profile, neck.",
    "anatomy_chest_gi": "Fetal chest (non-cardiac) and gastrointestinal anatomy.",
    "anatomy_spine": "Fetal spine anatomy.",
    "anatomy_urinary": "Fetal genitourinary anatomy: kidneys, bladder, ureters.",
    "anatomy_general": (
        "System-agnostic anatomy wrapper fields (main / detail / "
        "anomalies metadata) that apply across organ systems."
    ),
    "cardiac": (
        "Fetal cardiac anatomy and echocardiography measurements; "
        "heart-specific findings on both sides."
    ),
    "amniotic_fluid": (
        "Amniotic fluid index, single deepest pocket, and the GE "
        "amniotic-fluid measurement family."
    ),
    "placenta_cord": (
        "Placenta location and grading, umbilical cord findings, "
        "umbilical artery Doppler indices, and fetal-vessel data."
    ),
    "fetal_procedures": (
        "Invasive fetal procedures: amniocentesis, FBS/CVS, ectopic "
        "pregnancy management, other procedures."
    ),
    "fetus_core": (
        "Per-fetus identity (number, position, presentation, tone, "
        "activity), antepartum testing (NST, BPP)."
    ),
    "indication_impression": (
        "Free-text and coded exam indications, ICD-10 codes, and narrative impressions."
    ),
    "dating": ("Pregnancy dating: LMP, EDD, gestational age, agreed dating method."),
    "encounter": (
        "Exam-level metadata: date, location, signing, exam type, "
        "referring provider, accession, plus GE imaging-parameter "
        "and structured-report file blocks."
    ),
    "maternal_subject": (
        "Maternal demographics and history: patient block, "
        "obstetric history, family/anamnestic history, antenatal "
        "booking, screening tests."
    ),
    "non_fetal_gyn": (
        "Non-fetal gynecologic anatomy: adnexa, cervix, "
        "endomyometrial / uterine findings, uterine artery Doppler, "
        "gynecologic procedures."
    ),
    "_unclustered": (
        "Paths and identifiers that matched no cluster prefix. "
        "Expected to be empty; non-empty means clusters.yaml needs a new prefix."
    ),
}


TABLE_COLUMNS = [
    "concept_key",
    "observer_path",
    "observer_label_values",
    "observer_value_class",
    "observer_sample",
    "viewpoint_path",
    "viewpoint_short_label",
    "viewpoint_value_class",
    "viewpoint_sample",
    "notes",
]
