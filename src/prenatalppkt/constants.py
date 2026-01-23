from prenatalppkt.hpo.simple_term import SimpleTerm
from prenatalppkt.measurements.percentile_range import PercentileRange


DEFAULT_BPD_LOW = PercentileRange.between_5p_10p()
DEFAULT_BPD_HIGH = PercentileRange.between_90p_95p()

DECREASED_BPD_TERM = SimpleTerm(
    hpo_id="HP:0020259", hpo_label="Decreased biparietal diameter"
)
INCREASED_BPD_TERM = SimpleTerm(
    hpo_id="HP:0020260", hpo_label="Increased biparietal diameter"
)
ABNORMAL_BPD_TERM = SimpleTerm(
    hpo_id="HP:6001417", hpo_label="Abnormal biparietal diameter"
)


DEFAULT_OFD_LOW = PercentileRange.below_3p()
DEFULAT_OFD_HIGH = PercentileRange.above_97p()

DECREASED_OFD_TERM = SimpleTerm(
    hpo_id="HP:0020298", hpo_label="Decreased occipitofrontal diameter"
)
INCREASED_OFD_TERM = SimpleTerm(
    hpo_id="HP:0020299", hpo_label="Increased occipitofrontal diameter"
)
ABNORMAL_OFD_TERM = SimpleTerm(
    hpo_id="HP:0020297", hpo_label="Abnormal occipitofrontal diameter"
)
