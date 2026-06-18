"""Tests for the VCF scanner and the VcfVariant domain type."""

from __future__ import annotations

import dataclasses

import pytest

from prenatalppkt.genomics.vcf import VcfVariant, scan_vcf_text

_HEADER = "\n".join(
    [
        "##fileformat=VCFv4.2",
        "##reference=GRCh38",
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE1",
    ]
)


def _vcf(*data_lines: str, header: str = _HEADER) -> str:
    return header + "\n" + "\n".join(data_lines) + "\n"


def _variant(**overrides) -> VcfVariant:
    base = {
        "genome_assembly": "GRCh38",
        "chrom": "chr1",
        "pos": 100,
        "id": ".",
        "ref": "A",
        "alt": "T",
        "qual": ".",
        "filter": "PASS",
        "info": ".",
    }
    base.update(overrides)
    return VcfVariant(**base)


class TestVcfVariant:
    def test_holds_all_fields(self):
        v = _variant()
        assert v.chrom == "chr1"
        assert v.pos == 100
        assert v.ref == "A"
        assert v.alt == "T"
        assert v.genome_assembly == "GRCh38"

    def test_is_frozen(self):
        v = _variant()
        with pytest.raises(dataclasses.FrozenInstanceError):
            v.pos = 200  # type: ignore[misc]


class TestScanVcfText:
    def test_skips_headers_and_parses_records(self):
        text = _vcf(
            "chr1\t100\trs1\tA\tT\t50\tPASS\tDP=30\tGT\t0/1",
            "chr2\t200\t.\tG\tC\t.\t.\t.\tGT\t1/1",
        )
        variants = scan_vcf_text(text)
        assert len(variants) == 2
        assert variants[0].chrom == "chr1"
        assert variants[0].pos == 100
        assert variants[1].alt == "C"

    def test_reads_assembly_from_reference_header(self):
        variants = scan_vcf_text(_vcf("chr1\t1\t.\tA\tT\t.\t.\t."))
        assert variants[0].genome_assembly == "GRCh38"

    def test_assembly_param_used_when_no_header_token(self):
        text = "chr1\t1\t.\tA\tT\t.\t.\t.\n"
        variants = scan_vcf_text(text, genome_assembly="GRCh37")
        assert variants[0].genome_assembly == "GRCh37"

    def test_strips_format_and_sample_columns(self):
        """The FORMAT column and sample genotypes must not leak into INFO."""
        text = _vcf("chr1\t100\t.\tA\tT\t.\t.\tDP=30\tGT:AD\t0/1:5,6")
        v = scan_vcf_text(text)[0]
        assert v.info == "DP=30"
        assert "0/1" not in v.info
        assert not hasattr(v, "format")

    def test_skips_blank_and_short_lines(self):
        text = _vcf("", "chr1\t100\t.\tA", "chr1\t200\t.\tA\tT\t.\t.\t.")
        assert len(scan_vcf_text(text)) == 1
