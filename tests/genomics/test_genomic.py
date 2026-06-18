"""Tests for the Phenopacket v2 genomic builders."""

from __future__ import annotations

from prenatalppkt.genomics.genomic import to_vcf_record
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
