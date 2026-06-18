"""Tests for the VCF scanner and the VcfVariant domain type."""

from __future__ import annotations

import dataclasses
import gzip
import io
import tarfile
from pathlib import Path

import pytest

from prenatalppkt.genomics.vcf import (
    VcfVariant,
    scan_vcf_archive,
    scan_vcf_file,
    scan_vcf_text,
)

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


class TestScanVcfFile:
    def test_plaintext_file(self, tmp_path):
        text = _vcf("chr1\t100\trs1\tA\tT\t.\tPASS\t.")
        path = tmp_path / "sample.vcf"
        path.write_text(text)
        variants = scan_vcf_file(path)
        assert len(variants) == 1
        assert variants[0].genome_assembly == "GRCh38"

    def test_gzip_file_matches_plaintext(self, tmp_path):
        text = _vcf(
            "chr1\t100\trs1\tA\tT\t.\tPASS\t.\tGT\t0/1",
            "chr3\t300\t.\tC\tG\t.\t.\t.\tGT\t1/1",
        )
        plain = tmp_path / "sample.vcf"
        plain.write_text(text)
        gz = tmp_path / "sample.vcf.gz"
        gz.write_bytes(gzip.compress(text.encode("utf-8")))
        assert scan_vcf_file(gz) == scan_vcf_file(plain)
        assert len(scan_vcf_file(gz)) == 2


def _make_targz(path, members: dict[str, bytes]) -> None:
    with tarfile.open(path, "w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


class TestScanVcfArchive:
    def test_scans_vcf_members_and_skips_others(self, tmp_path):
        vcf_a = _vcf("chr1\t100\t.\tA\tT\t.\t.\t.").encode("utf-8")
        vcf_b_gz = gzip.compress(
            _vcf("chr2\t200\t.\tG\tC\t.\t.\t.\tGT\t0/1").encode("utf-8")
        )
        bundle = tmp_path / "twins.vcf.tar.gz"
        _make_targz(
            bundle,
            {
                "fetus_1.vcf": vcf_a,
                "fetus_2.vcf.gz": vcf_b_gz,
                "README.txt": b"not a vcf",
            },
        )
        result = scan_vcf_archive(bundle)
        assert set(result) == {"fetus_1.vcf", "fetus_2.vcf.gz"}
        assert result["fetus_1.vcf"][0].chrom == "chr1"
        assert result["fetus_2.vcf.gz"][0].pos == 200


_DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class TestCommittedFixtures:
    """The synthetic *.vcf fixtures parse and leak no sample genotypes."""

    def test_apple_sally(self):
        variants = scan_vcf_file(_DATA_DIR / "Apple_Sally.vcf")
        assert len(variants) == 3
        assert all(v.genome_assembly == "GRCh38" for v in variants)
        for v in variants:
            assert "0/1" not in v.info and "1/1" not in v.info

    def test_blue_sally(self):
        variants = scan_vcf_file(_DATA_DIR / "Blue_Sally.vcf")
        assert len(variants) == 2
        assert variants[1].ref == "G" and variants[1].alt == "GA"
