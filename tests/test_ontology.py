"""
test_ontology.py

Tests for HPO ontology download and lookup.
"""

import json
import pytest
from pathlib import Path
from prenatalppkt.ontology import HPO


def test_lookup_known_terms(tmp_path):
    # Fake hp.json with just two nodes
    fake_json = {
        "graphs": [
            {
                "nodes": [
                    {"id": "HP:0000252", "lbl": "Microcephaly"},
                    {"id": "HP:0000256", "lbl": "Macrocephaly"},
                ]
            }
        ]
    }
    fake_file = tmp_path / "hp.json"
    fake_file.write_text(json.dumps(fake_json))

    ontology = HPO(fake_file)

    assert ontology.get_label("HP:0000252") == "Microcephaly"
    assert ontology.get_id("Macrocephaly") == "HP:0000256"
    assert ontology.is_valid("HP:0000252")
    assert not ontology.is_valid("HP:9999999")
    assert ontology.search_label("cephaly") == ["HP:0000252", "HP:0000256"]


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        HPO(Path("not_there.json"))
