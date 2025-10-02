"""
constants.py

Ontology identifiers and fixed values for prenatal biometry mappings.
Keeping them centralized makes updates and maintenance easier.
"""

# Human Phenotype Ontology (HPO) term identifiers

HPO_MICROCEPHALY: str = "HP:0000252"
"""Microcephaly: head circumference significantly below expected size."""

HPO_MACROCEPHALY: str = "HP:0000256"
"""Macrocephaly: head circumference significantly above expected size."""

# New
HPO_SHORT_FEMUR = "HP:0011428"  # Short fetal femur length
HPO_LONG_FEMUR = "HP:9999999"  # Placeholder - if HPO doesn't define it, keep as custom
