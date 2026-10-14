"""Tests for the measurement registry and the name tables built from it."""

import textwrap
from pathlib import Path

import pytest
import yaml

from prenatalppkt.etl import constants, scan_type, term_bin_factory
from prenatalppkt.etl.constants import BiometryMeasurement
from prenatalppkt.etl.measurement_registry import REGISTRY, SOURCES, load_registry
from prenatalppkt.etl.term_bin_factory import TermBinFactory
from prenatalppkt.scripts import data_dict


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
            assert tuple(spec.guessed_aliases) == SOURCES


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
        assert spec.guessed_aliases["observer"] == ()

    def test_guessed_aliases_are_kept_apart_but_looked_up(self, tmp_path):
        path = _write(
            tmp_path,
            """
            Femur:
              role: required
              yaml_key: femur_length
              aliases:
                viewpoint_hl7: [FemurUndefinedLength]
              guessed_aliases:
                viewpoint_hl7: [FemurLength]
            """,
        )
        spec = load_registry(path)["Femur"]
        assert spec.aliases["viewpoint_hl7"] == ("FemurUndefinedLength",)
        assert spec.guessed_aliases["viewpoint_hl7"] == ("FemurLength",)
        assert spec.all_aliases("viewpoint_hl7") == (
            "FemurUndefinedLength",
            "FemurLength",
        )

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
                "unknown sources in aliases",
            ),
            (
                "role: optional\n  yaml_key: x\n  guessed_aliases:\n    fax: [X]",
                "unknown sources in guessed_aliases",
            ),
            (
                "role: optional\n  yaml_key: x\n  aliases:\n    observer: [X, X]",
                "duplicate observer alias",
            ),
            (
                "role: optional\n  yaml_key: x\n  aliases:\n    observer: [X]\n"
                "  guessed_aliases:\n    observer: [X]",
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

    def test_guessed_alias_shared_by_two_measurements_raises(self, tmp_path):
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
              guessed_aliases:
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


# Literal copies of every name table. A change here is a behavior change, so
# it should only ever come with a registry edit that means it.

_OBSERVER_NAME_MAP = {
    "HC": "HC",
    "BPD": "BPD",
    "AC": "AC",
    "Femur": "Femur",
    "FL": "Femur",
    "Nuchal Fold": "Nuchal Fold",
    "Cerebellum": "Cerebellum",
    "OFD": "OFD",
    "Humerus": "Humerus",
    "CRL": "CRL",
    "NT": "NT",
    "Tibia": "Tibia",
    "Fibula": "Fibula",
    "Radius": "Radius",
    "Ulna": "Ulna",
    "Foot": "Foot",
    "Cisterna Magna": "Cisterna Magna",
    "Nasal Bone": "Nasal Bone",
    "Lateral Vent left": "Lateral Vent left",
    "Lateral Vent right": "Lateral Vent right",
    "Biorbit": "Biorbit",
    "Mean Gest Sac": "Mean Gest Sac",
}
_VIEWPOINT_TEXT_NAME_MAP = {
    "HC": "HC",
    "BPD": "BPD",
    "AC": "AC",
    "Femur": "Femur",
    "Nuchal Fold": "Nuchal Fold",
    "Cerebellum": "Cerebellum",
    "OFD": "OFD",
    "Humerus": "Humerus",
    "Cisterna Magna": "Cisterna Magna",
    "Nasal Bone": "Nasal Bone",
    "Lateral Vent left": "Lateral Vent left",
    "Lateral Vent right": "Lateral Vent right",
    "Biorbit": "Biorbit",
}
_VIEWPOINT_HL7_NAME_MAP = {
    "HeadCircumference": "HC",
    "BiparietalDiameter": "BPD",
    "BiParietalDiameter": "BPD",
    "OccipitoFrontalDiameter": "OFD",
    "HumerusUndefinedLength": "Humerus",
    "TibiaUndefinedLength": "Tibia",
    "FibulaUndefinedLength": "Fibula",
    "TranscerebellarDiameter": "Cerebellum",
    "CrownRumpLength": "CRL",
    "NuchalTranslucency": "NT",
    "NuchalFoldThickness": "Nuchal Fold",
    "AbdominalCircumference": "AC",
    "FemurUndefinedLength": "Femur",
    "FemurLength": "Femur",
    "NuchalFold": "Nuchal Fold",
    "Cerebellum": "Cerebellum",
    "OccipitofrontalDiameter": "OFD",
    "HumerusLength": "Humerus",
    "CisternaMagna": "Cisterna Magna",
    "NasalBone": "Nasal Bone",
    "LateralVentricleLeft": "Lateral Vent left",
    "LateralVentricleRight": "Lateral Vent right",
    "BiorbitalDiameter": "Biorbit",
}
_GENERIC_NAME_MAP = {
    "hc": "HC",
    "head_circumference": "HC",
    "head circumference": "HC",
    "headcircumference": "HC",
    "bpd": "BPD",
    "biparietal_diameter": "BPD",
    "biparietal diameter": "BPD",
    "biparietaldiameter": "BPD",
    "ac": "AC",
    "abdominal_circumference": "AC",
    "abdominal circumference": "AC",
    "abdominalcircumference": "AC",
    "femur": "Femur",
    "fl": "Femur",
    "femur_length": "Femur",
    "femur length": "Femur",
    "femurlength": "Femur",
    "femurundefinedlength": "Femur",
    "nuchal": "Nuchal Fold",
    "nuchal_fold": "Nuchal Fold",
    "nuchal fold": "Nuchal Fold",
    "nuchalfold": "Nuchal Fold",
    "cerebellum": "Cerebellum",
    "ofd": "OFD",
    "occipitofrontal_diameter": "OFD",
    "occipitofrontal diameter": "OFD",
    "occipito-frontal diameter": "OFD",
    "occipitofrontaldiameter": "OFD",
    "humerus": "Humerus",
    "hl": "Humerus",
    "humerus_length": "Humerus",
    "humerus length": "Humerus",
    "humeruslength": "Humerus",
    "cisterna magna": "Cisterna Magna",
    "cisterna_magna": "Cisterna Magna",
    "cisternamagna": "Cisterna Magna",
    "nasal bone": "Nasal Bone",
    "nasal_bone": "Nasal Bone",
    "nasalbone": "Nasal Bone",
    "lateral vent left": "Lateral Vent left",
    "lateral ventricle left": "Lateral Vent left",
    "lateral_ventricle_left": "Lateral Vent left",
    "lateralventricleleft": "Lateral Vent left",
    "lateral vent right": "Lateral Vent right",
    "lateral ventricle right": "Lateral Vent right",
    "lateral_ventricle_right": "Lateral Vent right",
    "lateralventricleright": "Lateral Vent right",
    "biorbit": "Biorbit",
    "biorbital": "Biorbit",
    "biorbital_diameter": "Biorbit",
    "biorbital diameter": "Biorbit",
    "biorbitaldiameter": "Biorbit",
}
_NAME_TO_YAML = {
    "HC": "head_circumference",
    "BPD": "biparietal_diameter",
    "AC": "abdominal_circumference",
    "Femur": "femur_length",
    "OFD": "occipitofrontal_diameter",
    "CRL": "crown_rump_length",
    "NT": "nuchal_translucency",
    "Tibia": "tibia_length",
    "Fibula": "fibula_length",
    "Radius": "radius_length",
    "Ulna": "ulna_length",
    "Foot": "foot_length",
    "Humerus": "humerus_length",
    "Nuchal Fold": "nuchal_fold",
    "Cerebellum": "cerebellum",
    "Cisterna Magna": "cisterna_magna",
    "Nasal Bone": "nasal_bone",
    "Lateral Vent left": "lateral_ventricle_left",
    "Lateral Vent right": "lateral_ventricle_right",
    "Biorbit": "biorbital_diameter",
}
_REQUIRED_MEASUREMENTS = {"AC", "BPD", "Femur", "HC"}
_OPTIONAL_MEASUREMENTS = {
    "Biorbit",
    "Cerebellum",
    "Cisterna Magna",
    "Fibula",
    "Foot",
    "Humerus",
    "Lateral Vent left",
    "Lateral Vent right",
    "Mean Gest Sac",
    "Nasal Bone",
    "Nuchal Fold",
    "OFD",
    "Radius",
    "Tibia",
    "Ulna",
}
_DELIBERATELY_UNMAPPED_MEASUREMENTS = {"Mean Gest Sac"}
_T1_LABELS = {"CRL", "NT"}
_T2T3_REQUIRED_LABELS = {"AC", "BPD", "Femur", "HC"}


class TestTablesMatchRegistry:
    @pytest.mark.parametrize(
        "table, expected",
        [
            (constants.OBSERVER_NAME_MAP, _OBSERVER_NAME_MAP),
            (constants.VIEWPOINT_TEXT_NAME_MAP, _VIEWPOINT_TEXT_NAME_MAP),
            (constants.VIEWPOINT_HL7_NAME_MAP, _VIEWPOINT_HL7_NAME_MAP),
            (constants.GENERIC_NAME_MAP, _GENERIC_NAME_MAP),
        ],
        ids=["observer", "viewpoint_text", "viewpoint_hl7", "generic"],
    )
    def test_name_maps(self, table, expected):
        assert all(isinstance(m, BiometryMeasurement) for m in table.values())
        assert {label: m.value for label, m in table.items()} == expected

    def test_name_to_yaml(self):
        assert TermBinFactory._NAME_TO_YAML == _NAME_TO_YAML

    @pytest.mark.parametrize(
        "table, expected",
        [
            (term_bin_factory.REQUIRED_MEASUREMENTS, _REQUIRED_MEASUREMENTS),
            (term_bin_factory.OPTIONAL_MEASUREMENTS, _OPTIONAL_MEASUREMENTS),
            (
                term_bin_factory.DELIBERATELY_UNMAPPED_MEASUREMENTS,
                _DELIBERATELY_UNMAPPED_MEASUREMENTS,
            ),
            (scan_type.T1_LABELS, _T1_LABELS),
            (scan_type.T2T3_REQUIRED_LABELS, _T2T3_REQUIRED_LABELS),
        ],
        ids=["required", "optional", "unmapped", "t1", "t2t3"],
    )
    def test_name_sets(self, table, expected):
        assert table == expected


# The data dictionary's concept_aliases.yaml lists ViewPoint ids per concept
# independently of the registry. Each biometry measurement concept's ids must
# resolve, through the registry, to that concept's measurement.
_CONCEPT_ALIASES_PATH = Path(data_dict.__file__).parent / "concept_aliases.yaml"
_BIOMETRY_CONCEPT_MEASUREMENT = {
    "bpd": "BPD",
    "ac": "AC",
    "hc": "HC",
    "crl": "CRL",
    "femur": "Femur",
    "humerus": "Humerus",
    "nuchal_fold": "Nuchal Fold",
}


class TestConceptAliasesAgree:
    def _measurement_concepts(self):
        concepts = yaml.safe_load(_CONCEPT_ALIASES_PATH.read_text(encoding="utf-8"))
        for key, entry in concepts.items():
            parts = key.split(".")
            if parts[0] == "biometry" and parts[-1] == "measurement_mm":
                yield parts[1], (entry or {}).get("viewpoint") or []

    def test_every_biometry_concept_is_known(self):
        slugs = {slug for slug, _ in self._measurement_concepts()}
        assert slugs <= set(_BIOMETRY_CONCEPT_MEASUREMENT)

    def test_viewpoint_ids_resolve_to_the_concept_measurement(self):
        for slug, identifiers in self._measurement_concepts():
            for identifier in identifiers:
                base = identifier.split(".")[-1]
                resolved = constants.VIEWPOINT_HL7_NAME_MAP.get(base)
                assert resolved is not None, f"{identifier} is not in the registry"
                assert resolved.value == _BIOMETRY_CONCEPT_MEASUREMENT[slug], identifier
