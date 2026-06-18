"""Tests for `extract.clusters`: classify_observer and classify_viewpoint routing."""

from __future__ import annotations

import pytest

from prenatalppkt.scripts.data_dict.extract.clusters import (
    UNCLUSTERED,
    classify_observer,
    classify_viewpoint,
)
from prenatalppkt.scripts.data_dict.extract.models import Cluster


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
