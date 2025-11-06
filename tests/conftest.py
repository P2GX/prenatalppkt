# tests/conftest.py
import gzip
from pathlib import Path
import pytest
from prenatalppkt.hpo import HpoParser


DATA_DIR = Path(__file__).parent / "data"
HP_JSON_GZ = DATA_DIR / "hp.json.gz"


@pytest.fixture(scope="session")
def hpo_cr(tmp_path_factory):
   """Shared fixture: load and parse gzipped hp.json once per test session."""
   tmp_dir = tmp_path_factory.mktemp("hpo")
   json_path = tmp_dir / "hp.json"

   with (
       gzip.open(HP_JSON_GZ, "rt", encoding="utf-8") as f_in,
       open(json_path, "w", encoding="utf-8") as f_out,
   ):
       f_out.write(f_in.read())

   parser = HpoParser(hpo_json_file=str(json_path))
   return parser.get_hpo_concept_recognizer()