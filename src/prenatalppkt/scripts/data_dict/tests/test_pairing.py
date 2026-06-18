"""Tests for `extract.pairing`: token normalization, match-token sets, compatible classes, pair_fields."""

from __future__ import annotations

from prenatalppkt.scripts.data_dict.extract.models import ObserverField, ViewpointField
from prenatalppkt.scripts.data_dict.extract.pairing import (
    compatible_classes,
    normalize_token,
    observer_match_tokens,
    pair_fields,
    viewpoint_match_tokens,
)


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
