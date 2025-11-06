import pytest
from prenatalppkt.parser.observer.fetus.fetus_ratios_parser import FetusRatiosParser

sample_ratios_json = {
    "ratios": [
        {
            "label": "HC/AC",
            "value": 1.105,
            "decimal_paces": 2,
            "calculated_percentile": 0,
            "percentile_for_display": "",
            "print_in_report": 1,
            "range": "1.04 - 1.22",
            "fetus_number": 1,
        },
        {
            "label": "FL/BPD",
            "value": 75,
            "decimal_paces": 0,
            "calculated_percentile": 0,
            "percentile_for_display": "",
            "print_in_report": 1,
            "range": "71 - 87",
            "fetus_number": 1,
        },
    ]
}


def test_parse_ratios_basic():
    parser = FetusRatiosParser()
    data = parser.parse(sample_ratios_json)

    assert data is not None
    assert data.fetus_number == 1
    assert data.ratio_count == 2

    hc_ac = data.get_ratio_by_label("HC/AC")
    assert hc_ac is not None
    assert hc_ac.value == pytest.approx(1.105)
