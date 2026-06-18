"""VCF scanning into PHI-safe variant loci.

Reads VCF text, gzipped VCFs, and tar/tar.gz bundles, stripping each record to
the locus-level fields (CHROM POS ID REF ALT QUAL FILTER INFO) and dropping the
FORMAT column and any per-sample genotype columns, which can carry PHI. The
output is a list of `VcfVariant`, a rich domain type whose existence is the
proof the input parsed (parse, don't validate).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# The eight fixed VCF columns. Everything after INFO (FORMAT + per-sample
# genotype columns) is dropped on read - those columns can carry PHI.
_N_FIXED_COLUMNS = 8


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


def _assembly_from_header(line: str) -> str | None:
    """Pull a genome-assembly token from a `##` meta line, if present."""
    if line.startswith("##reference="):
        return line.split("=", 1)[1].strip() or None
    match = re.search(r"assembly=([^,>\s]+)", line)
    return match.group(1) if match else None


def scan_vcf_text(text: str, genome_assembly: str = "unknown") -> list[VcfVariant]:
    """Scan VCF text into locus-level `VcfVariant`s, dropping sample columns.

    Header (`##`) lines are inspected for a genome-assembly token, which
    overrides the `genome_assembly` fallback. The column header line (`#CHROM`)
    is skipped. Each data line is split to its first eight columns only; the
    FORMAT column and any per-sample genotype columns are discarded.
    """
    assembly = genome_assembly
    variants: list[VcfVariant] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("##"):
            found = _assembly_from_header(line)
            if found:
                assembly = found
            continue
        if line.startswith("#"):
            continue
        cols = raw.split("\t")
        if len(cols) < _N_FIXED_COLUMNS:
            continue
        chrom, pos, vid, ref, alt, qual, filt, info = cols[:_N_FIXED_COLUMNS]
        variants.append(
            VcfVariant(
                genome_assembly=assembly,
                chrom=chrom,
                pos=int(pos),
                id=vid,
                ref=ref,
                alt=alt,
                qual=qual,
                filter=filt,
                info=info,
            )
        )
    return variants
