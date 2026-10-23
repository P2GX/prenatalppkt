"""
Loads the measurement registry: one entry per biometry measurement, with its
role, its biometry-mappings key and the label each export format uses.

The per-format name maps, required/optional lists and YAML-key lookup are all
built from this registry. It deliberately works with plain strings (the
standard measurement names) so the modules that build those tables can import
it without an import cycle.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, Mapping, Optional, Tuple

import yaml

ROLES: FrozenSet[str] = frozenset({"required", "optional", "t1"})
SOURCES: Tuple[str, ...] = ("observer", "viewpoint_text", "viewpoint_hl7", "generic")
_FIELDS: FrozenSet[str] = frozenset({"role", "yaml_key", "unmapped_reason", "aliases"})

DEFAULT_REGISTRY_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "data"
    / "mappings"
    / "measurement_registry.yaml"
)


@dataclass(frozen=True)
class MeasurementSpec:
    """One measurement's registry entry, checked at load time."""

    name: str
    role: str
    yaml_key: Optional[str]
    unmapped_reason: Optional[str]
    aliases: Mapping[str, Tuple[str, ...]] = field(default_factory=dict)


def _parse_entry(name: str, entry: object) -> MeasurementSpec:
    if not isinstance(entry, dict):
        raise ValueError(f"{name}: entry must be a mapping")
    unknown = set(entry) - _FIELDS
    if unknown:
        raise ValueError(f"{name}: unknown fields {sorted(unknown)}")

    role = entry.get("role")
    if role not in ROLES:
        raise ValueError(f"{name}: role must be one of {sorted(ROLES)}, got {role!r}")

    yaml_key = entry.get("yaml_key")
    unmapped_reason = entry.get("unmapped_reason")
    if (yaml_key is None) == (unmapped_reason is None):
        raise ValueError(f"{name}: needs exactly one of yaml_key or unmapped_reason")

    raw_aliases = entry.get("aliases") or {}
    unknown_sources = set(raw_aliases) - set(SOURCES)
    if unknown_sources:
        raise ValueError(f"{name}: unknown alias sources {sorted(unknown_sources)}")

    aliases: Dict[str, Tuple[str, ...]] = {}
    for source in SOURCES:
        labels = tuple(str(label) for label in raw_aliases.get(source) or ())
        if len(set(labels)) != len(labels):
            raise ValueError(f"{name}: duplicate {source} alias")
        aliases[source] = labels

    return MeasurementSpec(
        name=name,
        role=role,
        yaml_key=yaml_key,
        unmapped_reason=unmapped_reason,
        aliases=aliases,
    )


def load_registry(path: Optional[Path] = None) -> Dict[str, MeasurementSpec]:
    """
    Load and check the measurement registry.

    Args:
        path: Registry YAML; defaults to data/mappings/measurement_registry.yaml

    Returns:
        Measurement specs keyed by standard measurement name, in file order

    Raises:
        ValueError: If an entry is malformed, or the same alias appears under
            two measurements for one source
    """
    with open(path or DEFAULT_REGISTRY_PATH, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    specs = {str(name): _parse_entry(str(name), entry) for name, entry in raw.items()}

    for source in SOURCES:
        owner: Dict[str, str] = {}
        for spec in specs.values():
            for label in spec.aliases[source]:
                if label in owner:
                    raise ValueError(
                        f"{source} alias {label!r} used by both {owner[label]} and {spec.name}"
                    )
                owner[label] = spec.name

    return specs


REGISTRY: Dict[str, MeasurementSpec] = load_registry()
