"""Tests for LOINC-coded Measurement emission in PhenotypicExporter.to_json."""

from __future__ import annotations

import json

from prenatalppkt.etl.term_bin_factory import TermBinFactory
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.phenotypic_export import PhenotypicExporter
from prenatalppkt.term_observation import TermObservation


def _build_four_core_bins():
    """Produce TermBins for HC/BPD/AC/Femur at percentile=50 + GA 26w."""
    factory = TermBinFactory()
    ga = GestationalAge(weeks=26, days=0)
    bins = []
    for name, value_mm in [
        ("HC", 250.0),
        ("BPD", 65.0),
        ("AC", 220.0),
        ("Femur", 50.0),
    ]:
        bins.append(
            factory.create_term_bin(
                name=name, value_mm=value_mm, percentile=50.0, gestational_age=ga
            )
        )
    return bins


def _matching_observations(bins):
    """One TermObservation per bin so to_json has phenotypicFeatures to emit."""
    ga = GestationalAge(weeks=26, days=0)
    return [
        TermObservation(
            hpo_id=b.hpo_id,
            hpo_label=b.hpo_label,
            category="normal_term",
            observed=not b.normal,
            gestational_age=ga,
            percentile=50.0,
        )
        for b in bins
    ]


def test_measurements_emitted_for_four_core_biometry():
    """HC/BPD/AC/FL all land as Measurement entries with their verified LOINC."""
    bins = _build_four_core_bins()
    observations = _matching_observations(bins)

    exporter = PhenotypicExporter()
    payload = json.loads(exporter.to_json(observations, term_bins=bins))

    assert "measurements" in payload
    assert len(payload["measurements"]) == 4

    loincs = {m["assay"]["id"] for m in payload["measurements"]}
    assert loincs == {
        "LOINC:11984-2",
        "LOINC:11820-8",
        "LOINC:11979-2",
        "LOINC:11963-6",
    }


def test_measurements_carry_mm_unit_and_raw_value():
    """Each Measurement uses UO:0000016 (mm) and preserves value_mm."""
    bins = _build_four_core_bins()
    observations = _matching_observations(bins)

    exporter = PhenotypicExporter()
    payload = json.loads(exporter.to_json(observations, term_bins=bins))

    by_loinc = {m["assay"]["id"]: m for m in payload["measurements"]}
    hc = by_loinc["LOINC:11984-2"]
    assert hc["value"]["quantity"]["unit"] == {
        "id": "UO:0000016",
        "label": "millimeter",
    }
    assert hc["value"]["quantity"]["value"] == 250.0


def test_phenotypic_features_and_measurements_both_present():
    """Same observation lands in both phenotypicFeatures and measurements."""
    bins = _build_four_core_bins()
    observations = _matching_observations(bins)

    exporter = PhenotypicExporter()
    payload = json.loads(exporter.to_json(observations, term_bins=bins))

    assert "phenotypicFeatures" in payload
    assert "measurements" in payload
    assert len(payload["phenotypicFeatures"]) == 4
    assert len(payload["measurements"]) == 4


def test_measurements_omitted_when_no_term_bins_supplied():
    """Back-compat: existing callers that don't pass term_bins get no measurements key."""
    bins = _build_four_core_bins()
    observations = _matching_observations(bins)

    exporter = PhenotypicExporter()
    payload = json.loads(exporter.to_json(observations))

    assert "measurements" not in payload
    assert "phenotypicFeatures" in payload
