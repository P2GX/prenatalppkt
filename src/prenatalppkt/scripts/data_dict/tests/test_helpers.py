"""Tests for `extract.build` helpers: joined, sample_text, viewpoint_type_signature, coverage."""

from __future__ import annotations

from prenatalppkt.scripts.data_dict.extract.build import (
    coverage,
    joined,
    sample_text,
    viewpoint_type_signature,
)
from prenatalppkt.scripts.data_dict.extract.models import ViewpointField


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
