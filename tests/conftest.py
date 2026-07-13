# tests/conftest.py
import gzip
from pathlib import Path
import pytest
from prenatalppkt.hpo import HpoParser


DATA_DIR = Path(__file__).parent / "data"
HP_JSON_GZ = DATA_DIR / "hp.json.gz"


@pytest.fixture(scope="session")
def hp_json_path(tmp_path_factory) -> str:
    """Decompress the bundled hp.json.gz once per session and return its path."""
    tmp_dir = tmp_path_factory.mktemp("hpo")
    json_path = tmp_dir / "hp.json"

    with (
        gzip.open(HP_JSON_GZ, "rt", encoding="utf-8") as f_in,
        open(json_path, "w", encoding="utf-8") as f_out,
    ):
        f_out.write(f_in.read())

    return str(json_path)


@pytest.fixture(scope="session")
def hpo_parser(hp_json_path) -> HpoParser:
    """Shared fixture: load and parse the bundled hp.json once per test session."""
    return HpoParser(hpo_json_file=hp_json_path)


@pytest.fixture(scope="session")
def hpo_cr(hpo_parser):
    return hpo_parser.get_hpo_concept_recognizer()
