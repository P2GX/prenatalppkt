"""Tests for ScanType classifier + UnsupportedScanTypeError."""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

import pytest

from prenatalppkt.etl.scan_type import (
    ScanType,
    UnsupportedScanTypeError,
    classify_fetus,
    detect_scan_type,
)

DATA_DIR = Path("tests/data")


def _fetus(labels: list[str]) -> dict:
    """Build a minimal Observer JSON dict with one fetus carrying the given labels."""
    return {
        "fetuses": [
            {
                "fetus": {"fetus_number": 1},
                "measurements": [{"label": lbl} for lbl in labels],
            }
        ]
    }


class TestDetectScanType:
    def test_full_biometry_is_t2_t3(self):
        assert (
            detect_scan_type(_fetus(["AC", "BPD", "HC", "Femur"]))
            == ScanType.T2_T3_BIOMETRY
        )

    def test_full_biometry_plus_extras_is_t2_t3(self):
        """Extra labels (Nuchal Fold, Humerus, etc.) don't change the classification."""
        assert (
            detect_scan_type(_fetus(["AC", "BPD", "HC", "Femur", "Nuchal Fold", "OFD"]))
            == ScanType.T2_T3_BIOMETRY
        )

    def test_fl_label_is_t2_t3(self):
        """Real Observer 7 exports label the femur 'FL'; it must classify as T2/T3."""
        assert (
            detect_scan_type(_fetus(["AC", "BPD", "HC", "FL"]))
            == ScanType.T2_T3_BIOMETRY
        )

    def test_fl_label_plus_extras_is_t2_t3(self):
        assert (
            detect_scan_type(_fetus(["AC", "BPD", "HC", "FL", "OFD", "Cerebellum"]))
            == ScanType.T2_T3_BIOMETRY
        )

    def test_crl_only_is_first_trimester(self):
        assert detect_scan_type(_fetus(["CRL"])) == ScanType.FIRST_TRIMESTER

    def test_nt_only_is_first_trimester(self):
        assert detect_scan_type(_fetus(["NT"])) == ScanType.FIRST_TRIMESTER

    def test_crl_and_nt_is_first_trimester(self):
        assert detect_scan_type(_fetus(["CRL", "NT"])) == ScanType.FIRST_TRIMESTER

    def test_partial_biometry_is_unknown(self):
        """HC alone (no T1 marker, no full T2/T3 set) is UNKNOWN."""
        assert detect_scan_type(_fetus(["HC"])) == ScanType.UNKNOWN

    def test_empty_measurements_is_unknown(self):
        assert detect_scan_type(_fetus([])) == ScanType.UNKNOWN

    def test_missing_fetuses_key_is_unknown(self):
        assert detect_scan_type({}) == ScanType.UNKNOWN

    def test_empty_fetuses_list_is_unknown(self):
        assert detect_scan_type({"fetuses": []}) == ScanType.UNKNOWN

    def test_accepts_name_field_alias(self):
        """Some exports use 'name' instead of 'label'. Both should classify the same."""
        data = {
            "fetuses": [
                {"measurements": [{"name": n} for n in ["AC", "BPD", "HC", "Femur"]]}
            ]
        }
        assert detect_scan_type(data) == ScanType.T2_T3_BIOMETRY


class TestClassifyFetus:
    """classify_fetus() takes a single fetus dict; detect_scan_type delegates to it."""

    def test_full_biometry_is_t2_t3(self):
        fetus = {
            "measurements": [{"label": lbl} for lbl in ["AC", "BPD", "HC", "Femur"]]
        }
        assert classify_fetus(fetus) == ScanType.T2_T3_BIOMETRY

    def test_fl_label_is_t2_t3(self):
        fetus = {"measurements": [{"label": lbl} for lbl in ["AC", "BPD", "HC", "FL"]]}
        assert classify_fetus(fetus) == ScanType.T2_T3_BIOMETRY

    def test_crl_only_is_first_trimester(self):
        assert (
            classify_fetus({"measurements": [{"label": "CRL"}]})
            == ScanType.FIRST_TRIMESTER
        )

    def test_partial_biometry_is_unknown(self):
        assert classify_fetus({"measurements": [{"label": "HC"}]}) == ScanType.UNKNOWN

    def test_no_measurements_is_unknown(self):
        assert classify_fetus({}) == ScanType.UNKNOWN

    def test_detect_scan_type_delegates_to_classify_fetus(self):
        """The two fetuses of a twin exam can classify differently."""
        data = {
            "fetuses": [
                {
                    "measurements": [
                        {"label": lbl} for lbl in ["AC", "BPD", "HC", "Femur"]
                    ]
                },
                {"measurements": [{"label": "CRL"}]},
            ]
        }
        assert detect_scan_type(data) == classify_fetus(data["fetuses"][0])
        assert classify_fetus(data["fetuses"][1]) == ScanType.FIRST_TRIMESTER


class TestUnsupportedScanTypeError:
    def test_is_value_error_subclass(self):
        """`except ValueError` should keep catching this for legacy callers."""
        assert issubclass(UnsupportedScanTypeError, ValueError)
        with pytest.raises(ValueError):
            raise UnsupportedScanTypeError("test")


class TestCorpus:
    """Each shipped fixture maps to a known ScanType - encodes the workflow shape."""

    EXPECTED: ClassVar[dict[str, ScanType]] = {
        "Apple_Sally_pretty.json": ScanType.T2_T3_BIOMETRY,
        "Blue_Sally_pretty.json": ScanType.T2_T3_BIOMETRY,
        "Charm_Sally_pretty.json": ScanType.T2_T3_BIOMETRY,
        "Eclair_Sally_pretty.json": ScanType.T2_T3_BIOMETRY,
        "Diva_Sally_pretty.json": ScanType.FIRST_TRIMESTER,
    }

    @pytest.mark.parametrize("fixture_name", sorted(EXPECTED.keys()))
    def test_corpus_classification(self, fixture_name):
        fixture = DATA_DIR / fixture_name
        data = json.loads(fixture.read_text(encoding="utf-8"))
        assert detect_scan_type(data) == self.EXPECTED[fixture_name]
