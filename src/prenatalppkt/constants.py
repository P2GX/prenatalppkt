

from prenatalppkt.hpo.simple_term import SimpleTerm
from prenatalppkt.measurements.percentile_range import PercentileRange


DEFAULT_BPD_LOW = PercentileRange.between_5p_10p()
DEFAULT_BPD_HIGH = PercentileRange.between_90p_95p()

DECREASED_BPD_TERM = SimpleTerm(hpo_id="HP:0020259", hpo_label="Decreased biparietal diameter")
INCREASED_BPD_TERM = SimpleTerm(hpo_id="HP:0020260", hpo_label="Increased biparietal diameter")
ABNORMAL_BPD_TERM = SimpleTerm(hpo_id="HP:6001417", hpo_label="Abnormal biparietal diameter")

