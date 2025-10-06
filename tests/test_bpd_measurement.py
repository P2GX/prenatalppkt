"""
Integration test for BiparietalDiameterMeasurement HPO term mapping.

Dataset reference:
------------------
NIHCD Fetal Growth Calculator (Non-Hispanic White)
Gestational Age: 20.86 weeks
Measurement: Biparietal Diameter
Percentile thresholds used (3rd-97th):
[145.25, 147.25, 150.37, 161.95, 174.41, 178.12, 180.56]
"""

from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.bpd_measurement import BiparietalDiameterMeasurement


def test_bpd_measurement_evaluate_all_bins():
    """
    Verify that BPD measurement correctly maps each percentile bin
    to the expected HPO term and observation flag.
    """
    thresholds = [145.25, 147.25, 150.37, 161.95, 174.41, 178.12, 180.56]
    ga = GestationalAge.from_weeks(20.86)
    ref = ReferenceRange(gestational_age=ga, percentiles=thresholds)
    bpd = BiparietalDiameterMeasurement()

    # <=3rd percentile -> decreased skull size
    obs = bpd.evaluate(ga, ref.evaluate(140.0))
    assert obs.hpo_term.name == "Decreased head circumference"
    assert obs.observed is True

    # 3rd-10th percentile -> abnormal skull size (mildly abnormal)
    obs = bpd.evaluate(ga, ref.evaluate(148.0))
    assert obs.hpo_term.name == "Abnormality of skull size"
    assert obs.observed is True

    # 10th-90th percentile -> normal range (parent term, not observed)
    obs = bpd.evaluate(ga, ref.evaluate(160.0))
    assert obs.hpo_term.name == "Abnormality of skull size"
    assert obs.observed is False

    # 90th-97th percentile -> abnormal skull size (mildly abnormal)
    obs = bpd.evaluate(ga, ref.evaluate(176.0))
    assert obs.hpo_term.name == "Abnormality of skull size"
    assert obs.observed is True

    # >=97th percentile -> increased skull size
    obs = bpd.evaluate(ga, ref.evaluate(185.0))
    assert obs.hpo_term.name == "Increased head circumference"
    assert obs.observed is True


def test_term_attributes_are_supported():
    """
    Ensure MinimalTerm factory objects expose expected attributes.

    This reflects the DefaultMinimalTerm dataclass used in hpotk>=0.5.5.
    """
    import hpotk

    term = hpotk.MinimalTerm.create_minimal_term(
        term_id="HP:0000252", name="Microcephaly", alt_term_ids=[], is_obsolete=False
    )
    assert hasattr(term, "identifier")
    assert hasattr(term, "name")
    assert hasattr(term, "alt_term_ids")
    assert hasattr(term, "is_obsolete")
