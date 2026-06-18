"""VCF scanning into PHI-safe variant loci.

Reads VCF text, gzipped VCFs, and tar/tar.gz bundles, stripping each record to
the locus-level fields (CHROM POS ID REF ALT QUAL FILTER INFO) and dropping the
FORMAT column and any per-sample genotype columns, which can carry PHI. The
output is a list of `VcfVariant`, a rich domain type whose existence is the
proof the input parsed (parse, don't validate).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VcfVariant:
    """A single VCF locus stripped to its non-sample fields.

    Field names mirror the GA4GH `VcfRecord` message so the protobuf builder is
    a 1:1 mapping. `pos` is 1-based as in the VCF spec.
    """

    genome_assembly: str
    chrom: str
    pos: int
    id: str
    ref: str
    alt: str
    qual: str
    filter: str
    info: str
