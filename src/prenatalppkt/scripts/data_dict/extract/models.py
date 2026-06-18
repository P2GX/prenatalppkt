"""Dataclasses for the data-dictionary extract pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Cluster:
    """One named cluster + its observer / viewpoint prefix lists."""

    name: str
    observer_prefixes: list[str] = field(default_factory=list)
    viewpoint_prefixes: list[str] = field(default_factory=list)


@dataclass
class ObserverField:
    """One Observer leaf, keyed by (path, single inherited label)."""

    path: str
    label: str = ""
    types: set[str] = field(default_factory=set)
    value_classes: set[str] = field(default_factory=set)
    samples: list[str] = field(default_factory=list)
    files: set[str] = field(default_factory=set)
    overflow: bool = False


@dataclass
class ViewpointField:
    """One HL7 OBX-3 primary identifier + its short/long labels."""

    identifier: str
    short_label: str = ""
    long_label: str = ""
    types: set[str] = field(default_factory=set)
    value_classes: set[str] = field(default_factory=set)
    obx_types: set[str] = field(default_factory=set)
    samples: list[str] = field(default_factory=list)
    files: set[str] = field(default_factory=set)
    overflow: bool = False
