"""LOINC workflow corpus test - one expected output per Observer JSON fixture.

Encodes how the Observer ETL + LOINC layer is expected to process each file
in ``tests/data/*_pretty.json`` so changes that drift from these expectations
fail loudly. Mirrors the existing fixture-driven pattern at
``tests/parser/observer/fetuses/test_fetus_measurements_parser.py``.

Four T2/T3 fixtures (Apple, Blue, Charm, Eclair) succeed and produce 4
LOINC-coded TermBins each. Diva is first-trimester (CRL only) so the
extractor raises ``ValueError`` from ``validate_required_measurements``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from prenatalppkt.etl.extractors import observer
from prenatalppkt.phenotypic_export import PhenotypicExporter

DATA_DIR = Path("tests/data")

# LOINC codes verified against loinc.org (see
# docs/local-only/PLAN-loinc-measurements-issue-57.md in cerebro).
EXPECTED_LOINC = {
    "HC": ("LOINC:11984-2", "Fetal Head Circumference US"),
    "BPD": ("LOINC:11820-8", "Fetal Head Diameter.biparietal US Active"),
    "AC": ("LOINC:11979-2", "Fetal Abdomen Circumference US"),
    "Femur": ("LOINC:11963-6", "Fetal Femur diaphysis [Length] US"),
}

# Raw-mm values per fixture (= cm-value * 10). pytest.approx absorbs the
# IEEE-754 artefacts from the cm->mm conversion in observer._convert_to_mm.
EXPECTED_VALUES_MM = {
    "Apple_Sally_pretty.json": {"HC": 250.0, "BPD": 66.8, "AC": 226.2, "Femur": 50.1},
    "Blue_Sally_pretty.json": {"HC": 203.1, "BPD": 58.1, "AC": 191.2, "Femur": 41.4},
    "Charm_Sally_pretty.json": {"HC": 316.2, "BPD": 93.1, "AC": 323.0, "Femur": 69.2},
    "Eclair_Sally_pretty.json": {"HC": 262.0, "BPD": 70.0, "AC": 255.0, "Femur": 51.0},
}


def _fixture_present(name: str) -> bool:
    return (DATA_DIR / name).exists()


@pytest.mark.parametrize(
    "fixture_name",
    [
        "Apple_Sally_pretty.json",
        "Blue_Sally_pretty.json",
        "Charm_Sally_pretty.json",
        "Eclair_Sally_pretty.json",
    ],
)
def test_corpus_fixture_yields_four_loinc_termbins(fixture_name):
    """Each T2/T3 fixture extracts 4 TermBins carrying LOINC + raw mm + GA."""
    if not _fixture_present(fixture_name):
        pytest.skip(f"{fixture_name} not found")

    term_bins = observer.extract_from_file(DATA_DIR / fixture_name)

    assert len(term_bins) == 4

    # Every TermBin must carry the new LOINC + raw-context fields.
    for tb in term_bins:
        assert tb.loinc_code is not None, f"missing loinc_code on {tb.hpo_id}"
        assert tb.loinc_label is not None
        assert tb.value_mm is not None
        assert tb.gestational_age_weeks is not None

    # The set of LOINC codes across the 4 bins is exactly HC/BPD/AC/Femur.
    loincs_present = {tb.loinc_code for tb in term_bins}
    assert loincs_present == {code for code, _ in EXPECTED_LOINC.values()}


@pytest.mark.parametrize(
    "fixture_name",
    [
        "Apple_Sally_pretty.json",
        "Blue_Sally_pretty.json",
        "Charm_Sally_pretty.json",
        "Eclair_Sally_pretty.json",
    ],
)
def test_corpus_fixture_raw_mm_matches_expected(fixture_name):
    """Raw mm values survive cm->mm conversion (with pytest.approx tolerance)."""
    if not _fixture_present(fixture_name):
        pytest.skip(f"{fixture_name} not found")

    term_bins = observer.extract_from_file(DATA_DIR / fixture_name)
    by_loinc = {tb.loinc_code: tb for tb in term_bins}
    expected = EXPECTED_VALUES_MM[fixture_name]

    for short_name, value_mm in expected.items():
        loinc_code, _ = EXPECTED_LOINC[short_name]
        tb = by_loinc[loinc_code]
        assert tb.value_mm == pytest.approx(value_mm, abs=1e-6), (
            f"{fixture_name} {short_name}: expected {value_mm}, got {tb.value_mm}"
        )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "Apple_Sally_pretty.json",
        "Blue_Sally_pretty.json",
        "Charm_Sally_pretty.json",
        "Eclair_Sally_pretty.json",
    ],
)
def test_corpus_fixture_to_measurement_dict_shape(fixture_name):
    """to_measurement_dict() emits a well-formed Phenopacket v2 Measurement."""
    if not _fixture_present(fixture_name):
        pytest.skip(f"{fixture_name} not found")

    term_bins = observer.extract_from_file(DATA_DIR / fixture_name)

    for tb in term_bins:
        msmt = tb.to_measurement_dict()
        assert msmt is not None
        assert msmt["assay"]["id"] == tb.loinc_code
        assert msmt["assay"]["label"] == tb.loinc_label
        assert msmt["value"]["quantity"]["unit"] == {
            "id": "UO:0000016",
            "label": "millimeter",
        }
        assert msmt["value"]["quantity"]["value"] == tb.value_mm


@pytest.mark.parametrize(
    "fixture_name",
    [
        "Apple_Sally_pretty.json",
        "Blue_Sally_pretty.json",
        "Charm_Sally_pretty.json",
        "Eclair_Sally_pretty.json",
    ],
)
def test_corpus_fixture_phenotypic_exporter_emits_measurements(fixture_name):
    """End-to-end: TermBins routed through PhenotypicExporter produce measurements[]."""
    if not _fixture_present(fixture_name):
        pytest.skip(f"{fixture_name} not found")

    term_bins = observer.extract_from_file(DATA_DIR / fixture_name)
    payload = json.loads(PhenotypicExporter().to_json([], term_bins=term_bins))

    assert "measurements" in payload
    assert len(payload["measurements"]) == 4

    loincs = {m["assay"]["id"] for m in payload["measurements"]}
    assert loincs == {code for code, _ in EXPECTED_LOINC.values()}

    for m in payload["measurements"]:
        assert m["value"]["quantity"]["unit"]["id"] == "UO:0000016"


def test_corpus_diva_first_trimester_raises():
    """Diva is CRL-only (T1); extractor raises rather than silently dropping."""
    fixture = DATA_DIR / "Diva_Sally_pretty.json"
    if not fixture.exists():
        pytest.skip("Diva_Sally_pretty.json not found")

    with pytest.raises(ValueError, match="Missing required biometry"):
        observer.extract_from_file(fixture)
