"""Tests for the measurement registry loader."""

import textwrap

import pytest

from prenatalppkt.etl.constants import BiometryMeasurement
from prenatalppkt.etl.measurement_registry import REGISTRY, SOURCES, load_registry


def _write(tmp_path, text):
    path = tmp_path / "registry.yaml"
    path.write_text(textwrap.dedent(text))
    return path


class TestShippedRegistry:
    def test_one_entry_per_biometry_measurement(self):
        assert set(REGISTRY) == BiometryMeasurement.all_values()

    def test_every_entry_lists_every_source(self):
        for spec in REGISTRY.values():
            assert tuple(spec.aliases) == SOURCES


class TestLoadRegistry:
    def test_valid_entry(self, tmp_path):
        path = _write(
            tmp_path,
            """
            HC:
              role: required
              yaml_key: head_circumference
              aliases:
                observer: [HC]
                generic: [hc, "head circumference"]
            """,
        )
        spec = load_registry(path)["HC"]
        assert spec.role == "required"
        assert spec.yaml_key == "head_circumference"
        assert spec.unmapped_reason is None
        assert spec.aliases["observer"] == ("HC",)
        assert spec.aliases["generic"] == ("hc", "head circumference")
        assert spec.aliases["viewpoint_hl7"] == ()

    @pytest.mark.parametrize(
        "body, message",
        [
            ("role: sometimes\n  yaml_key: x", "role must be one of"),
            ("role: optional", "exactly one of yaml_key or unmapped_reason"),
            (
                "role: optional\n  yaml_key: x\n  unmapped_reason: y",
                "exactly one of yaml_key or unmapped_reason",
            ),
            ("role: optional\n  yaml_key: x\n  colour: red", "unknown fields"),
            (
                "role: optional\n  yaml_key: x\n  aliases:\n    fax: [X]",
                "unknown alias sources",
            ),
            (
                "role: optional\n  yaml_key: x\n  aliases:\n    observer: [X, X]",
                "duplicate observer alias",
            ),
        ],
    )
    def test_malformed_entry_raises(self, tmp_path, body, message):
        path = tmp_path / "registry.yaml"
        path.write_text(f"X:\n  {body}\n")
        with pytest.raises(ValueError, match=message):
            load_registry(path)

    def test_alias_shared_by_two_measurements_raises(self, tmp_path):
        path = _write(
            tmp_path,
            """
            Femur:
              role: required
              yaml_key: femur_length
              aliases:
                observer: [FL]
            Foot:
              role: optional
              yaml_key: foot_length
              aliases:
                observer: [FL]
            """,
        )
        with pytest.raises(ValueError, match="'FL' used by both Femur and Foot"):
            load_registry(path)

    def test_same_alias_in_two_sources_is_fine(self, tmp_path):
        path = _write(
            tmp_path,
            """
            HC:
              role: required
              yaml_key: head_circumference
              aliases:
                observer: [HC]
                viewpoint_text: [HC]
            """,
        )
        assert load_registry(path)["HC"].aliases["viewpoint_text"] == ("HC",)
