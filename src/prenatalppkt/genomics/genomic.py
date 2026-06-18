"""Phenopacket v2 genomic builders.

Turns scanned `VcfVariant`s into the GA4GH genomic surfaces - `VcfRecord`,
`VariationDescriptor`, and an inert `Interpretation` scaffold - plus a
files-by-URI `File` entry. These are scaffolds: no VRS normalization and no real
ACMG / pathogenicity calls. The inert markers make that explicit downstream.
"""

from __future__ import annotations

from phenopackets import VariationDescriptor, VcfRecord

from prenatalppkt.genomics.vcf import VcfVariant


def to_vcf_record(variant: VcfVariant) -> VcfRecord:
    """Map a `VcfVariant` onto a GA4GH `VcfRecord` message (1:1 fields)."""
    return VcfRecord(
        genome_assembly=variant.genome_assembly,
        chrom=variant.chrom,
        pos=variant.pos,
        id=variant.id,
        ref=variant.ref,
        alt=variant.alt,
        qual=variant.qual,
        filter=variant.filter,
        info=variant.info,
    )


def to_variation_descriptor(
    variant: VcfVariant, descriptor_id: str
) -> VariationDescriptor:
    """Wrap a `VcfVariant` as a `VariationDescriptor` (vcf_record + label).

    Inert scaffold: the VRS `variation` field is left empty - only the
    `vcf_record` and a human-readable `label` are populated.
    """
    return VariationDescriptor(
        id=descriptor_id,
        label=f"{variant.chrom}:{variant.pos} {variant.ref}>{variant.alt}",
        vcf_record=to_vcf_record(variant),
    )
