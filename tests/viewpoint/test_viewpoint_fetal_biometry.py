import typing

import pytest
from prenatalppkt.parser.viewpoint.sections import (
    ViewpointFetalBiometryParser,
)





@pytest.fixture
def lines() -> typing.List[str]:
    """
    Fixture representing the NIHCD percentile cutoffs for BPD at 20.86 weeks.
    Thresholds correspond to:
        3rd, 5th, 10th, 50th, 90th, 95th, 97th percentiles.
    """
    lines = [
        " ",
        "BPD                                                         76.6                    mm                         30w 5d                     <1%                    Hadlock",
"OFD                                                         103.3                  mm                         30w 3d                     2%                       Nicolaides",
"HC                                                           285.7                  mm                         30w 4d                      <1%                    Chervenak",
"AC                                                           289.6                  mm                         33w 0d                      2%                      Hadlock",
"Femur                                                      65.0                    mm                         33w 4d                      3%                      Hadlock",
"Fetal Weight Calculation:",
"EFW                                                        2,042                  g                                                             2%",
"EFW (lb,oz)                                              4 lb 8                  oz",
"EFW by                                                     Hadlock (BPD-HC-AC-FL)",
"Extremities / Bony Struc Biometry:",
"FL / HC                                                    0.23",
 " "]
    return lines

def test_bpd(lines: typing.List[str]):
    parser = ViewpointFetalBiometryParser(lines=lines)
    assert parser is not None
    bpd = parser.bpd
    assert bpd is not None
    assert not bpd.normal

def test_ofd(lines: typing.List[str]):
    parser = ViewpointFetalBiometryParser(lines=lines)
    ofd = parser.ofd
    assert ofd is not None
    assert not ofd.normal
