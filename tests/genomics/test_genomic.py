"""Tests for the Phenopacket v2 genomic builders."""

from __future__ import annotations

from google.protobuf.json_format import MessageToJson, Parse
from phenopackets import AcmgPathogenicityClassification, Interpretation, Phenopacket

from prenatalppkt.genomics.genomic import (
    build_genomic_interpretation,
    build_vcf_file_entry,
    to_variation_descriptor,
    to_vcf_record,
)
from prenatalppkt.genomics.vcf import VcfVariant


def _variant(**overrides) -> VcfVariant:
    base = {
        "genome_assembly": "GRCh38",
        "chrom": "chr7",
        "pos": 200000,
        "id": "rs0000001",
        "ref": "C",
        "alt": "T",
        "qual": "99",
        "filter": "PASS",
        "info": "DP=45",
    }
    base.update(overrides)
    return VcfVariant(**base)


class TestToVcfRecord:
    def test_maps_all_fields(self):
        rec = to_vcf_record(_variant())
        assert rec.genome_assembly == "GRCh38"
        assert rec.chrom == "chr7"
        assert rec.pos == 200000
        assert rec.id == "rs0000001"
        assert rec.ref == "C"
        assert rec.alt == "T"
        assert rec.filter == "PASS"
        assert rec.info == "DP=45"


class TestToVariationDescriptor:
    def test_sets_id_label_and_vcf_record(self):
        vd = to_variation_descriptor(_variant(), descriptor_id="var-1")
        assert vd.id == "var-1"
        assert vd.label == "chr7:200000 C>T"
        assert vd.vcf_record.chrom == "chr7"

    def test_variation_left_empty(self):
        """Inert scaffold: no VRS variation is populated."""
        vd = to_variation_descriptor(_variant(), descriptor_id="var-1")
        assert not vd.HasField("variation")


class TestBuildVcfFileEntry:
    def test_sets_uri_and_default_format(self):
        f = build_vcf_file_entry("file:///data/Apple_Sally.vcf")
        assert f.uri == "file:///data/Apple_Sally.vcf"
        assert f.file_attributes["fileFormat"] == "VCF"

    def test_merges_extra_attributes(self):
        f = build_vcf_file_entry(
            "file:///x.vcf", attributes={"genomeAssembly": "GRCh38"}
        )
        assert f.file_attributes["genomeAssembly"] == "GRCh38"
        assert f.file_attributes["fileFormat"] == "VCF"


class TestBuildGenomicInterpretation:
    def test_one_genomic_interpretation_per_variant(self):
        variants = [_variant(), _variant(pos=300, alt="G")]
        interp = build_genomic_interpretation(
            variants, subject_id="fetus-1", interpretation_id="interp-1"
        )
        gis = interp.diagnosis.genomic_interpretations
        assert len(gis) == 2
        assert gis[0].subject_or_biosample_id == "fetus-1"

    def test_inert_markers(self):
        interp = build_genomic_interpretation(
            [_variant()], subject_id="fetus-1", interpretation_id="interp-1"
        )
        assert interp.progress_status == Interpretation.ProgressStatus.UNKNOWN_PROGRESS
        gi = interp.diagnosis.genomic_interpretations[0]
        assert gi.interpretation_status == gi.InterpretationStatus.CANDIDATE
        vi = gi.variant_interpretation
        assert (
            vi.acmg_pathogenicity_classification
            == AcmgPathogenicityClassification.NOT_PROVIDED
        )

    def test_disease_unset_without_argument(self):
        interp = build_genomic_interpretation(
            [_variant()], subject_id="fetus-1", interpretation_id="interp-1"
        )
        assert not interp.diagnosis.HasField("disease")

    def test_round_trips_through_json_on_a_phenopacket(self):
        """File + Interpretation survive MessageToJson -> Parse on a Phenopacket."""
        variant = _variant()
        pp = Phenopacket(id="demo")
        pp.files.append(build_vcf_file_entry("file:///demo.vcf"))
        pp.interpretations.append(
            build_genomic_interpretation(
                [variant], subject_id="fetus-1", interpretation_id="interp-1"
            )
        )
        reloaded = Parse(MessageToJson(pp), Phenopacket())
        assert reloaded.files[0].uri == "file:///demo.vcf"
        rec = (
            reloaded.interpretations[0]
            .diagnosis.genomic_interpretations[0]
            .variant_interpretation.variation_descriptor.vcf_record
        )
        assert rec.chrom == variant.chrom
        assert rec.pos == variant.pos
