import pytest
from prenatalppkt.parser.observer.fetus.fetus_efw_parser import FetusEfwParser

sample_efw_json = {
    "efws": [
        {
            "fetus_number": 1,
            "label": "EFW (AC, FL, HC)",
            "value": 1014.828,
            "decimal_paces": 0,
            "calculated_percentile": 55.6,
            "percentile_for_display": "56%",
            "print_in_report": 1,
            "range": "",
        },
        {
            "fetus_number": 1,
            "label": "EFW (AC, FL)",
            "value": 1042.214,
            "decimal_paces": 0,
            "calculated_percentile": 63.7,
            "percentile_for_display": "64%",
            "print_in_report": 0,
            "range": "",
        },
    ]
}


def test_parse_efw_basic():
    parser = FetusEfwParser()
    data = parser.parse(sample_efw_json)

    assert data is not None
    assert data.fetus_number == 1
    assert data.efw_count == 2

    efw = data.get_efw_by_label("EFW (AC, FL, HC)")
    assert efw is not None
    assert efw.value == pytest.approx(1014.828)
    assert efw.percentile_for_display == "56%"
