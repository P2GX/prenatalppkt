"""
Tests for TermBinFactory.

Tests the factory's ability to create TermBin objects from raw measurements
using existing percentile range and mapping infrastructure.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prenatalppkt.etl.term_bin_factory import (
    TermBinFactory,
    validate_required_measurements,
)
from prenatalppkt.gestational_age import GestationalAge


@pytest.fixture
def factory():
    """Create a TermBinFactory instance for testing."""
    # Uses default path: data/mappings/biometry_hpo_mappings.yaml
    f = TermBinFactory()
    return f


class TestTermBinFactory:
    """
    Test suite for TermBinFactory.

    Tests the factory using its internal _HPO_MAPPINGS (no mocking needed).
    """

    def test_create_term_bin_basic(self, factory):
        """
        Test creating TermBin from basic measurement (microcephaly case).
        """
        term_bin = factory.create_term_bin(
            name="HC",
            value_mm=180.0,
            percentile=2.0,
            gestational_age=GestationalAge(weeks=27, days=1),
        )

        assert term_bin is not None

        # HPO metadata comes from config bin
        assert term_bin.hpo_id == "HP:0000252"
        assert term_bin.hpo_label == "Microcephaly"
        assert term_bin.normal is False

        # Description is runtime, measurement-specific
        assert "180.0 mm" in term_bin.description
        assert "(2.0%)" in term_bin.description
        assert "27w1d" in term_bin.description

    def test_create_term_bin_normal_range(self, factory):
        """
        Test creating TermBin for normal percentile range.
        """
        term_bin = factory.create_term_bin(
            name="HC",
            value_mm=250.0,
            percentile=50.0,
            gestational_age=GestationalAge(weeks=26, days=0),
        )
        assert term_bin is not None
        assert term_bin.hpo_id == "HP:0000240"
        assert term_bin.normal is True
        assert "250.0 mm" in term_bin.description
        assert "(50.0%)" in term_bin.description

    def test_create_term_bin_with_all_fields(self, factory):
        """
        Test creating TermBin with all optional fields.
        """
        term_bin = factory.create_term_bin(
            name="HC",
            value_mm=233.7,
            percentile=36.0,
            gestational_age=GestationalAge(weeks=25, days=1),
            method="Hadlock",
            fetus_number=1,
        )

        assert term_bin is not None

        # Description should carry GA, method, and fetus number
        assert "25w1d" in term_bin.description
        assert "(Hadlock)" in term_bin.description
        assert "[Fetus 1]" in term_bin.description

    def test_create_term_bin_invalid_percentile(self, factory):
        """
        Test that invalid percentile raises error.
        """
        with pytest.raises(ValueError, match="Percentile must be 0-100"):
            factory.create_term_bin(name="HC", value_mm=200.0, percentile=150.0)

    def test_create_term_bin_threads_loinc_and_raw_value(self, factory):
        """Runtime TermBin carries LOINC, value_mm, and fractional GA weeks."""
        term_bin = factory.create_term_bin(
            name="HC",
            value_mm=233.7,
            percentile=50.0,
            gestational_age=GestationalAge(weeks=25, days=1),
        )

        assert term_bin is not None
        assert term_bin.loinc_code == "LOINC:11984-2"
        assert term_bin.loinc_label == "Fetal Head Circumference US"
        assert term_bin.value_mm == 233.7
        assert term_bin.gestational_age_weeks == pytest.approx(25 + 1 / 7)

    def test_create_term_bin_no_ga_leaves_ga_weeks_none(self, factory):
        """When gestational_age is omitted, the GA float field stays None."""
        term_bin = factory.create_term_bin(name="HC", value_mm=233.7, percentile=50.0)

        assert term_bin is not None
        assert term_bin.gestational_age_weeks is None
        assert term_bin.value_mm == 233.7

    def test_create_term_bin_loinc_codes_per_measurement(self, factory):
        """All four core biometry measurements carry their verified LOINC code."""
        cases = {
            "HC": "LOINC:11984-2",
            "BPD": "LOINC:11820-8",
            "AC": "LOINC:11979-2",
            "Femur": "LOINC:11963-6",
        }
        for name, expected in cases.items():
            term_bin = factory.create_term_bin(
                name=name,
                value_mm=50.0,
                percentile=50.0,
                gestational_age=GestationalAge(weeks=20, days=0),
            )
            assert term_bin is not None, f"{name} bin not created"
            assert term_bin.loinc_code == expected, (
                f"{name}: expected {expected}, got {term_bin.loinc_code}"
            )

    def test_create_term_bin_optional_no_mapping(self, factory):
        """
        Test that unmapped optional measurement returns None.
        """
        term_bin = factory.create_term_bin(
            # Mean Gest Sac is the one optional measurement with no real
            # HPO term possible (none exists for "gestational sac");
            # every other optional measurement has a real mapping.
            name="Mean Gest Sac",
            value_mm=60.0,
            percentile=50.0,
        )

        assert term_bin is None

    @pytest.mark.parametrize(
        "name,concern_percentile,concern_hpo,concern_label,"
        "reference_percentile,reference_hpo,reference_label",
        [
            (
                "Tibia",
                1.9,
                "HP:0005736",
                "Short tibia",
                50.0,
                "HP:0002992",
                "Abnormal tibia morphology",
            ),
            (
                "Fibula",
                1.9,
                "HP:0003038",
                "Fibular hypoplasia",
                50.0,
                "HP:0002991",
                "Abnormal fibula morphology",
            ),
            (
                "Radius",
                1.9,
                "HP:0002984",
                "Hypoplasia of the radius",
                50.0,
                "HP:0002818",
                "Abnormal morphology of the radius",
            ),
            (
                "Ulna",
                0.1,
                "HP:0003022",
                "Hypoplasia of the ulna",
                50.0,
                "HP:0040071",
                "Abnormal morphology of ulna",
            ),
            (
                "Foot",
                0.1,
                "HP:0001773",
                "Short foot",
                50.0,
                "HP:0001760",
                "Abnormal foot morphology",
            ),
            (
                "Humerus",
                1.9,
                "HP:0005792",
                "Short humerus",
                50.0,
                "HP:0031095",
                "Abnormal humerus morphology",
            ),
            (
                "Cerebellum",
                1.9,
                "HP:0001321",
                "Cerebellar hypoplasia",
                50.0,
                "HP:0001317",
                "Abnormal cerebellum morphology",
            ),
            (
                "Nuchal Fold",
                96.0,
                "HP:0000474",
                "Thickened nuchal skin fold",
                50.0,
                "HP:0000474",
                "Thickened nuchal skin fold",
            ),
            (
                "Cisterna Magna",
                96.0,
                "HP:0011427",
                "Enlarged fetal cisterna magna",
                50.0,
                "HP:0011427",
                "Enlarged fetal cisterna magna",
            ),
            (
                "Nasal Bone",
                1.9,
                "HP:0025707",
                "Hypoplastic fetal nasal bone",
                50.0,
                "HP:0010939",
                "Abnormal nasal bone morphology",
            ),
            (
                "Lateral Vent left",
                96.0,
                "HP:0002119",
                "Ventriculomegaly",
                50.0,
                "HP:0030047",
                "Abnormal lateral ventricle morphology",
            ),
            (
                "Lateral Vent right",
                96.0,
                "HP:0002119",
                "Ventriculomegaly",
                50.0,
                "HP:0030047",
                "Abnormal lateral ventricle morphology",
            ),
            (
                # Biorbital diameter row A: the low-extreme (Hypotelorism)
                # direction is the "concern" here.
                "Biorbit",
                1.9,
                "HP:0000601",
                "Hypotelorism",
                50.0,
                "HP:0000316",
                "Hypertelorism",
            ),
            (
                # Biorbital diameter row B: the high-extreme (Hypertelorism)
                # direction is the "concern" here. Same reference point as
                # row A (percentile 50 always resolves to the same bin
                # regardless of which direction a given row is testing).
                "Biorbit",
                96.0,
                "HP:0000316",
                "Hypertelorism",
                50.0,
                "HP:0000316",
                "Hypertelorism",
            ),
        ],
    )
    def test_create_term_bin_percentile_based_measurements(
        self,
        factory,
        name,
        concern_percentile,
        concern_hpo,
        concern_label,
        reference_percentile,
        reference_hpo,
        reference_label,
    ):
        """One unified table for every measurement with real percentile
        bins, regardless of which direction (low, high, or both) is
        clinically concerning - a "concern" percentile/term pair and a
        "reference" (usually normal) percentile/term pair per row, same
        two checks for every row. Humerus/Cerebellum share the long-bone
        shape unchanged (low=specific hypoplasia term, else=generic
        bidirectional term); Nuchal Fold/Cisterna Magna are one-
        directional (high only, same term both places, normal flag
        differs); Nasal Bone is low-only; Lateral Vent is high-only with
        a different term than its own reference; Biorbit has two real,
        opposite-direction terms and gets two rows, one per direction."""
        concern_bin = factory.create_term_bin(
            name=name, value_mm=42.0, percentile=concern_percentile
        )
        assert concern_bin is not None
        assert concern_bin.hpo_id == concern_hpo
        assert concern_bin.hpo_label == concern_label
        assert concern_bin.normal is False

        reference_bin = factory.create_term_bin(
            name=name, value_mm=42.0, percentile=reference_percentile
        )
        assert reference_bin is not None
        assert reference_bin.hpo_id == reference_hpo
        assert reference_bin.hpo_label == reference_label
        assert reference_bin.normal is True

    def test_create_term_bin_all_required_measurements(self, factory):
        """
        Test that all required measurements have HPO mappings.
        """
        ga = GestationalAge(weeks=26, days=0)

        # All required measurements should produce valid TermBins
        for name in ["HC", "BPD", "AC", "Femur"]:
            term_bin = factory.create_term_bin(
                name=name, value_mm=100.0, percentile=50.0, gestational_age=ga
            )
            assert term_bin is not None, f"{name} should have HPO mapping"
            assert term_bin.hpo_id.startswith("HP:"), f"{name} HPO ID invalid"

    def test_create_term_bin_extreme_percentiles(self, factory):
        """
        Test HPO selection for extreme percentiles.
        """
        ga = GestationalAge(weeks=26, days=0)

        # Very low percentile -> decreased term
        low_bin = factory.create_term_bin(
            name="HC", value_mm=150.0, percentile=1.0, gestational_age=ga
        )
        assert low_bin.hpo_id == "HP:0000252"  # Microcephaly
        assert low_bin.normal is False

        # Very high percentile -> increased term
        high_bin = factory.create_term_bin(
            name="HC", value_mm=350.0, percentile=99.0, gestational_age=ga
        )
        assert high_bin.hpo_id == "HP:0000256"  # Macrocephaly
        assert high_bin.normal is False


class TestValidateRequiredMeasurements:
    """
    Test validation of required measurements.
    """

    def test_all_required_present(self):
        """
        Test validation passes with all required measurements.
        """
        term_bins = [
            MagicMock(description="HC: 250.0 mm (42%)"),
            MagicMock(description="BPD: 63.2 mm (36%)"),
            MagicMock(description="AC: 226.2 mm (55%)"),
            MagicMock(description="Femur: 50.1 mm (46%)"),
        ]

        # Should not raise
        validate_required_measurements(term_bins)

    def test_missing_required_measurement(self):
        """
        Test validation fails with missing required measurement.
        """
        term_bins = [
            MagicMock(description="HC: 250.0 mm (42%)"),
            MagicMock(description="BPD: 63.2 mm (36%)"),
            # Missing AC and Femur
        ]

        with pytest.raises(ValueError, match="Missing required biometry measurements"):
            validate_required_measurements(term_bins)

    def test_error_message_lists_missing(self):
        """
        Test error message lists missing measurements.
        """
        term_bins = [MagicMock(description="HC: 250.0 mm (42%)")]

        with pytest.raises(ValueError) as exc_info:
            validate_required_measurements(term_bins)

        error_msg = str(exc_info.value)
        assert "AC" in error_msg
        assert "BPD" in error_msg
        assert "Femur" in error_msg

    def test_optional_measurements_not_required(self):
        """
        Test that optional measurements don't affect validation.
        """
        term_bins = [
            MagicMock(description="HC: 250.0 mm (42%)"),
            MagicMock(description="BPD: 63.2 mm (36%)"),
            MagicMock(description="AC: 226.2 mm (55%)"),
            MagicMock(description="Femur: 50.1 mm (46%)"),
            MagicMock(description="Nuchal Fold: 4.5 mm (10%)"),  # Optional
        ]

        # Should not raise
        validate_required_measurements(term_bins)


class TestTermBinFactoryIntegration:
    """
    Integration tests with real mappings.
    """

    @pytest.mark.skipif(
        not (
            Path(__file__).parent.parent.parent
            / "data"
            / "mappings"
            / "biometry_hpo_mappings.yaml"
        ).exists(),
        reason="Mapping file not found",
    )
    def test_create_with_real_mappings(self):
        """
        Test creating TermBins with real mapping file.
        """
        factory = TermBinFactory()

        # Test microcephaly case (HC below 3rd percentile)
        term_bin = factory.create_term_bin(name="HC", value_mm=180.0, percentile=2.0)

        assert term_bin is not None
        assert term_bin.normal is False
        assert "microcephaly" in term_bin.hpo_label.lower()
