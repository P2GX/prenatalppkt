"""Tests for the VCF scanner and the VcfVariant domain type."""

from __future__ import annotations

import dataclasses

import pytest

from prenatalppkt.genomics.vcf import VcfVariant


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
