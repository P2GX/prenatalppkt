"""Tests for `extract_all.py`: type detection, label-split walker, OBX parsing,
clustering, value-class inference, pairing, and concept_key lookup."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from prenatalppkt.scripts.data_dict.extract_all import (
    UNCLUSTERED,
    Cluster,
    ObserverField,
    ViewpointField,
    build_rows,
    classify_observer,
    classify_viewpoint,
    compatible_classes,
    coverage,
    display_hl7_value,
    hl7_observed_type,
    hl7_value_class,
    joined,
    json_type,
    load_concept_aliases,
    normalize_token,
    observer_match_tokens,
    pair_fields,
    parse_obx_line,
    sample_text,
    value_class,
    viewpoint_match_tokens,
    viewpoint_type_signature,
    walk_observer,
)


# -----------------------
# json_type
# -----------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "null"),
        (True, "bool"),
        (False, "bool"),
        (1, "int"),
        (0, "int"),
        (3.14, "float"),
        ("hello", "str"),
        ("45%", "str"),
        ("20w 3d", "str"),
    ],
)
def test_json_type_canonical_shapes(value, expected):
    """All canonical JSON value shapes classify into the right raw token."""
    assert json_type(value) == expected


# -----------------------
# value_class (semantic)
# -----------------------


@pytest.mark.parametrize(
    ("value", "path", "expected"),
    [
        (None, "", "empty"),
        ("", "", "empty"),
        (True, "", "boolean"),
        (12, "", "integer"),
        (12.5, "", "decimal"),
        ("56%", "", "percentile"),
        ("<5%", "", "percentile"),
        (">95%", "", "percentile"),
        ("24w 0d", "", "weeks_days"),
        ("20250923", "Exam.ExamDate", "date"),
        ("2025-09-23", "", "date"),
        ("normal", "", "coded_text"),
        ("123456", "exam.exm_time", "time"),
    ],
)
def test_value_class_covers_common_shapes(value, path, expected):
    """Semantic classifier picks up percentiles, weeks+days, dates, integers, etc."""
    assert value_class(value, path) == expected


def test_value_class_long_string_is_free_text():
    """Strings longer than the coded-text cutoff fall into free_text."""
    long_text = "x" * 81
    assert value_class(long_text) == "free_text"


# -----------------------
# Cluster classification
# -----------------------


@pytest.fixture
def clusters():
    """Two-cluster fixture exercising first-match-wins and the unclustered fallback."""
    return [
        Cluster("first", observer_prefixes=["fetuses[]"]),
        Cluster("second", observer_prefixes=["fetuses[].measurements[]"]),
        Cluster("vp", viewpoint_prefixes=["SkullFetus"]),
        Cluster(
            "anatomy",
            observer_prefixes=["fetuses[].anatomy[]"],
            viewpoint_prefixes=["BrainFetus", "FaceFetus"],
        ),
    ]


def test_classify_observer_first_match_wins(clusters):
    """The first cluster whose prefix list contains a string-prefix hit wins."""
    assert classify_observer("fetuses[].measurements[].value", clusters) == "first"


def test_classify_observer_unmatched_path_is_unclustered(clusters):
    """A path matching no prefix lands in the _unclustered bucket."""
    assert classify_observer("hist_phys_vitals.weight", clusters) == UNCLUSTERED


def test_classify_viewpoint_matches_prefix(clusters):
    """HL7 identifiers route through the same first-match-wins logic."""
    assert classify_viewpoint("SkullFetus.BPD", clusters) == "vp"
    assert classify_viewpoint("FaceFetus.Profile", clusters) == "anatomy"
    assert classify_viewpoint("WarningMessage", clusters) == UNCLUSTERED


# -----------------------
# Observer walker (label-split)
# -----------------------


def test_walk_observer_records_scalar_leaves_and_labels():
    """The walker records each scalar leaf keyed by (path, inherited-label)."""
    fields: dict[tuple[str, str], ObserverField] = {}
    walk_observer(
        {"fetuses": [{"measurements": [{"label": "BPD", "value": 6.1}]}]},
        "",
        "case.json",
        fields,
    )
    assert ("fetuses[].measurements[].value", "BPD") in fields
    record = fields[("fetuses[].measurements[].value", "BPD")]
    assert record.label == "BPD"
    assert "float" in record.types
    assert "decimal" in record.value_classes
    assert record.files == {"case.json"}


def test_walk_observer_splits_measurements_by_label():
    """Two measurements with different labels become two distinct records."""
    fields: dict[tuple[str, str], ObserverField] = {}
    walk_observer(
        {
            "fetuses": [
                {
                    "measurements": [
                        {"label": "BPD", "value": 45.2},
                        {"label": "AC", "value": 163.0},
                    ]
                }
            ]
        },
        "",
        "case.json",
        fields,
    )
    assert ("fetuses[].measurements[].value", "BPD") in fields
    assert ("fetuses[].measurements[].value", "AC") in fields
    assert fields[("fetuses[].measurements[].value", "BPD")].label == "BPD"
    assert fields[("fetuses[].measurements[].value", "AC")].label == "AC"


def test_walk_observer_dedupes_samples_across_files():
    """A repeated value should not appear twice in the sample list."""
    fields: dict[tuple[str, str], ObserverField] = {}
    walk_observer({"k": "v"}, "", "a.json", fields)
    walk_observer({"k": "v"}, "", "b.json", fields)
    record = fields[("k", "")]
    assert record.samples == ["v"]
    assert record.files == {"a.json", "b.json"}


def test_walk_observer_dict_dives_into_children():
    """Dict containers do not become leaf records; their scalar children do."""
    fields: dict[tuple[str, str], ObserverField] = {}
    walk_observer(
        {"exam": {"fetus_count": 1, "site_name": "CUIMC"}}, "", "file1.json", fields
    )
    assert ("exam.fetus_count", "") in fields
    assert ("exam.site_name", "") in fields
    assert ("exam", "") not in fields
    assert ("fetuses", "") not in fields


# -----------------------
# OBX parsing
# -----------------------


def test_parse_obx_keeps_identifier_short_long_and_value():
    """A canonical OBX-3 splits into (type, identifier, short_label, long_label, value)."""
    parsed = parse_obx_line(
        "OBX|1|NM|SkullFetus.BiparietalDiameter^BPD^Biparietal diameter"
        "|Fetus1|62.1^62.1|mm&millimeters||||||||20250923"
    )
    assert parsed == (
        "NM",
        "SkullFetus.BiparietalDiameter",
        "BPD",
        "Biparietal diameter",
        "62.1^62.1",
    )


def test_parse_obx_line_non_obx_returns_none():
    """Non-OBX segments are skipped."""
    assert parse_obx_line("MSH|^~\\&|GE|...\r\n") is None
    assert parse_obx_line("PID|1||12345\r\n") is None


def test_parse_obx_line_too_short_returns_none():
    """A truncated OBX line missing required fields is rejected."""
    assert parse_obx_line("OBX|1|NM|FOO\r\n") is None


def test_display_hl7_value_renders_secondary_when_distinct():
    """If the second caret-segment carries unit context, render `primary (secondary)`."""
    assert display_hl7_value("163^24w 0d") == "163 (24w 0d)"
    assert display_hl7_value("0^<1%") == "0 (<1%)"
    assert display_hl7_value("") == ""


def test_display_hl7_value_unwraps_doubled_numeric():
    """When primary == secondary (typical NM), the display collapses to the primary."""
    assert display_hl7_value("45.2^45.2") == "45.2"
    assert display_hl7_value("just text") == "just text"


# -----------------------
# HL7 type / value-class inference
# -----------------------


@pytest.mark.parametrize(
    ("raw_value", "obx_type", "expected"),
    [
        ("", "ST", "null"),
        ("45.2^45.2", "NM", "float"),
        ("62^62", "NM", "int"),
        ("Normal", "ST", "str"),
    ],
)
def test_hl7_observed_type(raw_value, obx_type, expected):
    """OBX-5 value + OBX-2 declared type map to a JSON-shape token."""
    assert hl7_observed_type(raw_value, obx_type) == expected


def test_hl7_value_class_uses_display_percentile():
    """Percentile and weeks_days fire from the second caret-segment / identifier hints."""
    assert hl7_value_class("0^<1%", "Fetus.VP_Field_Percentile", "NM") == "percentile"
    assert (
        hl7_value_class("168^24w 0d", "ExamOBDating.GestationalAgeDaysAgreed", "NM")
        == "weeks_days"
    )


def test_hl7_value_class_numeric_split():
    """An NM value with a decimal point reads as decimal, otherwise integer."""
    assert hl7_value_class("45.2^45.2", "SkullFetus.BPD", "NM") == "decimal"
    assert hl7_value_class("45^45", "SkullFetus.BPD", "NM") == "integer"


# -----------------------
# Pairing
# -----------------------


def test_normalize_token_camel_and_punct():
    """CamelCase splits at boundaries and punctuation collapses to underscores."""
    assert normalize_token("BiparietalDiameter") == "biparietal_diameter"
    assert normalize_token("Crown-Rump Length") == "crown_rump_length"


def test_observer_match_tokens_includes_label_unconditionally():
    """When a label is set, it is added to the observer's matchable token set."""
    record = ObserverField("fetuses[].measurements[].value", label="BPD")
    tokens = observer_match_tokens(record)
    assert "bpd" in tokens
    assert "value" in tokens


def test_viewpoint_match_tokens_includes_leaf_short_long():
    """Viewpoint tokens cover identifier leaf, short_label, and long_label."""
    record = ViewpointField(
        "SkullFetus.BiparietalDiameter",
        short_label="BPD",
        long_label="Biparietal diameter",
    )
    tokens = viewpoint_match_tokens(record)
    assert "biparietal_diameter" in tokens
    assert "bpd" in tokens


def test_compatible_classes_treats_numeric_as_inter_compatible():
    """integer / decimal / percentile pair across the numeric family even with no exact overlap."""
    assert compatible_classes({"integer"}, {"decimal"})
    assert compatible_classes({"percentile"}, {"decimal"})
    assert not compatible_classes({"coded_text"}, {"decimal"})


def test_pairing_is_conservative():
    """A label-matched observer pairs with the corresponding viewpoint; the rest stay unpaired."""
    observer = ObserverField(
        "fetuses[].measurements[].value", value_classes={"decimal"}, label="BPD"
    )
    viewpoint = ViewpointField(
        "SkullFetus.BiparietalDiameter", short_label="BPD", value_classes={"decimal"}
    )
    unrelated = ViewpointField(
        "SkullFetus.HeadCircumference", short_label="HC", value_classes={"decimal"}
    )
    pairs = pair_fields([observer], [unrelated, viewpoint])
    assert pairs[0] == (observer, viewpoint)
    assert pairs[1] == (None, unrelated)


def test_pairing_label_split_pairs_each_measurement():
    """The label-split walker output lets BPD and AC each pair independently."""
    obs_bpd = ObserverField(
        "fetuses[].measurements[].value", value_classes={"decimal"}, label="BPD"
    )
    obs_ac = ObserverField(
        "fetuses[].measurements[].value", value_classes={"decimal"}, label="AC"
    )
    vp_bpd = ViewpointField(
        "SkullFetus.BiparietalDiameter", short_label="BPD", value_classes={"decimal"}
    )
    vp_ac = ViewpointField(
        "AbdomenFetus.AbdominalCircumference",
        short_label="AC",
        value_classes={"decimal"},
    )
    pairs = pair_fields([obs_bpd, obs_ac], [vp_ac, vp_bpd])
    matched = {(obs.label, vp.identifier) for obs, vp in pairs if obs and vp}
    assert matched == {
        ("BPD", "SkullFetus.BiparietalDiameter"),
        ("AC", "AbdomenFetus.AbdominalCircumference"),
    }


# -----------------------
# Row formatting
# -----------------------


def test_joined_sorted_pipe_separated():
    """A set renders pipe-joined in deterministic sorted order."""
    assert joined({"int", "float", "null"}) == "float|int|null"


def test_sample_text_appends_overflow_marker():
    """A truncated sample list shows the trailing `|...` marker."""
    assert sample_text(["a", "b"], overflow=True) == "a|b|..."
    assert sample_text(["a"], overflow=False) == "a"
    assert sample_text([], overflow=False) == ""


def test_viewpoint_type_signature_combines_observed_and_obx_declared():
    """Viewpoint cells embed the declared OBX-2 type in parens."""
    record = ViewpointField("X", types={"float", "null"}, obx_types={"NM"})
    assert viewpoint_type_signature(record) == "float|null (NM)"


def test_viewpoint_type_signature_no_obx_falls_back_to_observed():
    """If no OBX-2 types were ever seen, only observed types render."""
    record = ViewpointField("X", types={"str"})
    assert viewpoint_type_signature(record) == "str"


def test_coverage_formats_present_over_total():
    """File coverage renders as `present/total`."""
    assert coverage({"a.json", "b.json", "c.json"}, 5) == "3/5"


# -----------------------
# Concept aliases (Plan 13)
# -----------------------


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
