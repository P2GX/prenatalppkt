# Exomiser input shape

[Exomiser](https://github.com/exomiser/Exomiser) ranks candidate genes and
variants from a phenotype description plus a VCF. This page covers how a
`prenatalppkt`-built Phenopacket and its genomics scaffold map onto what
Exomiser actually reads on the command line.

## What Exomiser reads, and what it doesn't

Exomiser's `analyse` command takes a sample phenopacket and a VCF as two
separate inputs:

```bash
java -jar exomiser-cli-*.jar analyse \
    --sample phenopacket.json \
    --vcf sample.vcf \
    --assembly GRCh38
```

- `--sample` reads `phenotypicFeatures[]` for HPO terms - this is the only
  part of the Phenopacket Exomiser uses for phenotype matching. Anything
  `prenatalppkt`'s builders put into `phenotypicFeatures[]` (biometry
  percentile bins, anatomy findings, clinical impression terms) is visible
  to Exomiser's phenotype-driven prioritisation.
- `--vcf` supplies the actual variant calls. This is a separate CLI
  argument, not read out of the Phenopacket.
- A `files[]` entry built by `build_vcf_file_entry()` is **informational
  only** - it records that a VCF exists and its assembly as Phenopacket
  provenance, but Exomiser does not read `files[]` to find the VCF. The
  `--vcf` flag is what actually wires the variant data in.

## The proband name has to match the VCF's sample column

Exomiser matches the phenotype's subject to a genotype column in the VCF by
exact string equality: the Phenopacket's `subject.id` must equal one of the
VCF's own sample column names (the `#CHROM ... FORMAT <sample-name>` header
line). If they don't match, Exomiser fails with an
`IllegalStateException: Proband sample name '<id>' is not found in the VCF
sample`, not a silent mismatch.

This means a Phenopacket built for its own subject-id conventions (e.g. an
accession-derived `<accession>-fetus-1`) will not automatically line up with
whatever sample name a VCF happens to carry (a sequencer or pipeline-assigned
identifier, often unrelated to the accession). Reconciling the two is the
caller's responsibility - `prenatalppkt` does not rewrite either side to make
them match.

## Minimal example

Building a Phenopacket with genomic data attached, using the genomics
scaffold's public API (see [](../reference/functions.md) for the full
function list):

```python
from prenatalppkt.genomics import (
    VcfVariant,
    build_genomic_interpretation,
    build_vcf_file_entry,
)

variant = VcfVariant(
    genome_assembly="GRCh38",
    chrom="chr7",
    pos=200000,
    id="rs0000001",
    ref="C",
    alt="T",
    qual="99",
    filter="PASS",
    info="DP=45",
)

phenopacket.files.append(
    build_vcf_file_entry(
        "file:///data/sample.vcf",
        attributes={"genomeAssembly": "GRCh38"},
    )
)
phenopacket.interpretations.append(
    build_genomic_interpretation(
        [variant],
        subject_id=phenopacket.subject.id,
        interpretation_id="interp-1",
    )
)
```

`build_genomic_interpretation()` produces an inert scaffold
(`UNKNOWN_PROGRESS`, `CANDIDATE`, ACMG `NOT_PROVIDED`) - it records that a
variant was scanned, not a diagnosis. Interpreting Exomiser's actual ranked
output back into a Phenopacket is a separate step, outside this library's
scope.

The corresponding invocation, once `phenopacket.subject.id` matches the
VCF's own sample name:

```bash
java -jar exomiser-cli-*.jar analyse \
    --sample phenopacket.json \
    --vcf /data/sample.vcf \
    --assembly GRCh38 \
    --output-directory results/
```

See [](../reference/index.md) for where the genomics scaffold sits relative
to the rest of the library.
