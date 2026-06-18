"""Tests for `extract.concept_aliases`: load_concept_aliases."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from prenatalppkt.scripts.data_dict.extract.concept_aliases import load_concept_aliases


@pytest.fixture
def aliases_yaml(tmp_path: Path) -> Path:
    """Minimal concept_aliases.yaml fixture covering an Observer+HL7 concept."""
    content = textwrap.dedent(
        """\
        biometry.bpd.measurement_mm:
          description: Biparietal diameter, raw mm
          observer:
            - path: fetuses[].measurements[].value
              label: BPD
          viewpoint:
            - SkullFetus.BiparietalDiameter

        biometry.bpd.percentile:
          description: BPD percentile
          observer:
            - path: fetuses[].measurements[].calculated_percentile
              label: BPD

        fetus.gender:
          description: Fetal sex
          observer:
            - path: fetuses[].fetus.gender
              label: ""
          viewpoint:
            - BabyPatientData.Gender
        """
    )
    path = tmp_path / "concept_aliases.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_concept_aliases_builds_both_lookup_tables(aliases_yaml: Path):
    """Both observer and viewpoint lookups are populated from one YAML file."""
    obs, vp = load_concept_aliases(aliases_yaml)
    assert (
        obs[("fetuses[].measurements[].value", "BPD")] == "biometry.bpd.measurement_mm"
    )
    assert (
        obs[("fetuses[].measurements[].calculated_percentile", "BPD")]
        == "biometry.bpd.percentile"
    )
    assert obs[("fetuses[].fetus.gender", "")] == "fetus.gender"
    assert vp["SkullFetus.BiparietalDiameter"] == "biometry.bpd.measurement_mm"
    assert vp["BabyPatientData.Gender"] == "fetus.gender"


def test_load_concept_aliases_missing_label_defaults_to_empty(aliases_yaml: Path):
    """An entry with label: \"\" lands under the empty-label key, not under None."""
    obs, _ = load_concept_aliases(aliases_yaml)
    assert ("fetuses[].fetus.gender", "") in obs
    assert ("fetuses[].fetus.gender", None) not in obs
