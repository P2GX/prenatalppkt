"""Tests for `extract.build.build_rows`: concept_key stamping + CSV column header."""

from __future__ import annotations

from prenatalppkt.scripts.data_dict.extract.build import build_rows
from prenatalppkt.scripts.data_dict.extract.models import (
    Cluster,
    ObserverField,
    ViewpointField,
)


def test_build_rows_stamps_concept_key_on_observer_row():
    """Observer side hits the alias map; row's concept_key matches."""
    clusters = [Cluster("biometry", observer_prefixes=["fetuses[].measurements[]"])]
    observer = ObserverField(
        "fetuses[].measurements[].value",
        label="BPD",
        types={"float"},
        value_classes={"decimal"},
        files={"a.json"},
    )
    rows = build_rows(
        {("fetuses[].measurements[].value", "BPD"): observer},
        {},
        clusters,
        1,
        0,
        observer_concepts={
            ("fetuses[].measurements[].value", "BPD"): "biometry.bpd.measurement_mm"
        },
        viewpoint_concepts={},
    )
    assert len(rows) == 1
    assert rows[0][0] == "biometry.bpd.measurement_mm"


def test_build_rows_stamps_concept_key_from_viewpoint_when_observer_unmapped():
    """When only the HL7 side is in the alias map, the row picks up its concept_key."""
    clusters = [Cluster("biometry", viewpoint_prefixes=["SkullFetus"])]
    viewpoint = ViewpointField(
        "SkullFetus.BiparietalDiameter",
        short_label="BPD",
        types={"float"},
        value_classes={"decimal"},
        files={"phenotype_1.txt"},
    )
    rows = build_rows(
        {},
        {"SkullFetus.BiparietalDiameter": viewpoint},
        clusters,
        0,
        1,
        observer_concepts={},
        viewpoint_concepts={
            "SkullFetus.BiparietalDiameter": "biometry.bpd.measurement_mm"
        },
    )
    assert len(rows) == 1
    assert rows[0][0] == "biometry.bpd.measurement_mm"


def test_build_rows_empty_concept_key_when_unmapped():
    """A row whose Observer leaf and HL7 identifier are both unmapped gets `""`."""
    clusters = [Cluster("biometry", observer_prefixes=["fetuses[].measurements[]"])]
    observer = ObserverField(
        "fetuses[].measurements[].value",
        label="Mystery",
        types={"float"},
        value_classes={"decimal"},
        files={"a.json"},
    )
    rows = build_rows(
        {("fetuses[].measurements[].value", "Mystery"): observer}, {}, clusters, 1, 0
    )
    assert len(rows) == 1
    assert rows[0][0] == ""


def test_csv_columns_lead_with_concept_key():
    """The 16-column CSV puts concept_key first."""
    from prenatalppkt.scripts.data_dict.extract_all import CSV_COLUMNS

    assert CSV_COLUMNS[0] == "concept_key"
    assert CSV_COLUMNS[1] == "cluster"
    assert len(CSV_COLUMNS) == 16
