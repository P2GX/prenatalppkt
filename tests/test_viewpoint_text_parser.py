#
from pathlib import Path
from prenatalppkt.parser.viewpoint.viewpoint_text_parser import ViewpointTextParse

parent_dir = Path(__file__).parent
viewpoint_file = parent_dir / "data" / "viewpoint_1.txt"


def test_ctor():
    parser = ViewpointTextParse(input=viewpoint_file)
    sections = parser._section_d
    assert len(sections) > 0
