"""
ETL module for prenatal phenotype packet extraction, transformation, and loading.

This module provides a streamlined, modular approach to:
- Extract biometry measurements from Observer JSON, ViewPoint text, and ViewPoint HL7
- Transform measurements into standardized formats
- Load data into term bins for HPO mapping

Example:
   TODO @VarenyaJ
"""

from prenatalppkt.etl.models.biometry import Biometry, BiometryCollection
from prenatalppkt.etl.extractors.base import BiometryExtractor
from prenatalppkt.etl.extractors.observer import ObserverExtractor
from prenatalppkt.etl.extractors.viewpoint_text import ViewPointTextExtractor

__all__ = [
    # Data models
    "Biometry",
    "BiometryCollection",
    # Base classes
    "BiometryExtractor",
    # Concrete extractors
    "ObserverExtractor",
    "ViewPointTextExtractor",
]

__version__ = "0.1.0"
