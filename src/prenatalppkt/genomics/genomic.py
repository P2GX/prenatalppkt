"""Phenopacket v2 genomic builders.

Turns scanned `VcfVariant`s into the GA4GH genomic surfaces - `VcfRecord`,
`VariationDescriptor`, and an inert `Interpretation` scaffold - plus a
files-by-URI `File` entry. These are scaffolds: no VRS normalization, and no
ACMG / pathogenicity calls unless the caller supplies real ones. The inert
markers make the no-call default explicit downstream.
"""

from __future__ import annotations

from phenopackets import (
    AcmgPathogenicityClassification,
    Diagnosis,
    File,
    GenomicInterpretation,
    Interpretation,
    OntologyClass,
    VariantInterpretation,
    VariationDescriptor,
    VcfRecord,
)

from prenatalppkt.genomics.vcf import VcfVariant

# Inert markers - the scaffold asserts no real progress, candidacy, or pathogenicity.
_PROGRESS_UNKNOWN = Interpretation.ProgressStatus.UNKNOWN_PROGRESS
_STATUS_CANDIDATE = GenomicInterpretation.InterpretationStatus.CANDIDATE
_ACMG_NOT_PROVIDED = AcmgPathogenicityClassification.NOT_PROVIDED


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


def build_vcf_file_entry(uri: str, attributes: dict[str, str] | None = None) -> File:
    """Build a Phenopacket `File` entry referencing a VCF by URI.

    Always tags `fileFormat=VCF`; caller-supplied `attributes` (e.g.
    `genomeAssembly`) are merged in.
    """
    file_attributes = {"fileFormat": "VCF"}
    if attributes:
        file_attributes.update(attributes)
    return File(uri=uri, file_attributes=file_attributes)


def build_genomic_interpretation(
    variants: list[VcfVariant],
    subject_id: str,
    interpretation_id: str,
    disease: OntologyClass | None = None,
    acmg_classifications: list[AcmgPathogenicityClassification.ValueType] | None = None,
) -> Interpretation:
    """Build a genomic `Interpretation` from scanned variants.

    One `GenomicInterpretation` per variant, each carrying the variant as a
    `VariationDescriptor`. `interpretation_status` stays `CANDIDATE` and
    `progress_status` stays `UNKNOWN_PROGRESS` regardless - this builds the
    variant-level interpretation shape, not a diagnosis.

    `acmg_classifications`, if given, must be the same length as `variants`
    (one classification per variant, same order) - a real classification a
    caller has already computed (e.g. from a variant-prioritisation tool).
    Omitted or `None` keeps every variant `NOT_PROVIDED`, the original inert
    default. `disease` is left unset unless supplied, to avoid a placeholder
    CURIE.
    """
    if acmg_classifications is not None and len(acmg_classifications) != len(variants):
        raise ValueError(
            f"acmg_classifications has {len(acmg_classifications)} entries, "
            f"variants has {len(variants)} - must match 1:1"
        )

    genomic_interpretations = [
        GenomicInterpretation(
            subject_or_biosample_id=subject_id,
            interpretation_status=_STATUS_CANDIDATE,
            variant_interpretation=VariantInterpretation(
                acmg_pathogenicity_classification=(
                    acmg_classifications[i]
                    if acmg_classifications is not None
                    else _ACMG_NOT_PROVIDED
                ),
                variation_descriptor=to_variation_descriptor(
                    variant, descriptor_id=f"{interpretation_id}-var-{i + 1}"
                ),
            ),
        )
        for i, variant in enumerate(variants)
    ]

    diagnosis = Diagnosis(genomic_interpretations=genomic_interpretations)
    if disease is not None:
        diagnosis.disease.CopyFrom(disease)

    return Interpretation(
        id=interpretation_id, progress_status=_PROGRESS_UNKNOWN, diagnosis=diagnosis
    )
