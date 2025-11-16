from pathlib import Path
from prenatalppkt.parser.viewpoint.sections.viewpoint_impression_parse import (
    ViewpointImpressionParser,
)
from prenatalppkt.hpo.simple_term import SimpleTerm


IMPRESSION_LINES = [
    "The patient is referred ... by",
    "...gravidarum and maternal obesity...baby...",
    "...medication. The results of her NIPT...detected.",
    "",
    "The fetal biometry continues ...AC",
    "...at the...deepest",
    "...of measure X.",
    "",
    "-Doppler...",
    "...adaptation... result.",
    "- Doppler.",
    "- Unable to ...",
    "",
    "Prominent ... is observed. This ...",
    "obstruction.",
    "",
    "The patient is informed of the findings by ... result.",
    "Narrative",
]

EXPECTED_SENTENCES = [
    "The patient is referred ... by ...gravidarum and maternal obesity...baby... ...medication. The results of her NIPT...detected.",
    "The fetal biometry continues ...AC ...at the...deepest ...of measure X.",
    "-Doppler... ...adaptation... result.",
    "- Doppler.",
    "- Unable to ...",
    "Prominent ... is observed. This ... obstruction.",
    "The patient is informed of the findings by ... result.",
    "Narrative",
]


def test_viewpoint_impression_parser():
    parser = ViewpointImpressionParser(IMPRESSION_LINES)

    assert parser.paragraphs == EXPECTED_SENTENCES
    assert parser.impression == " ".join(EXPECTED_SENTENCES)


def test_viewpoint_impression_parser_hpo_terms_from_file(hpo_cr):
    data_path = (
        Path(__file__).resolve().parent.parent / "data" / "viewpoint_text_test.txt"
    )
    lines = data_path.read_text().splitlines()

    parser = ViewpointImpressionParser(lines, hpo_cr)

    expected = SimpleTerm(hpo_id="HP:0012418", hpo_label="Hypoxemia")
    found_ids = {t.hpo_id for t in parser.hpo_terms}

    assert expected.hpo_id in found_ids, (
        f"Expected {expected.hpo_id} not found. Extracted: {parser.hpo_terms}"
    )
