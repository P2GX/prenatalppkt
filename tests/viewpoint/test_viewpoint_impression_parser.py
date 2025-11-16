from prenatalppkt.parser.viewpoint.sections.viewpoint_impression_parse import (
    ViewpointImpressionParser,
)


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

    # Sentence-by-sentence correctness
    assert parser.paragraphs == EXPECTED_SENTENCES

    # Flattened impression correctness
    assert parser.impression == " ".join(EXPECTED_SENTENCES)
