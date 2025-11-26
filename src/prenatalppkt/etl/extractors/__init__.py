"""
Biometry extractors for different input formats.

Each extractor provides:
- extract(data, factory) -> List[TermBin]
- extract_from_file(filepath, factory) -> List[TermBin]

No abstract base class - each extractor is standalone.
"""

from prenatalppkt.etl.extractors import observer
from prenatalppkt.etl.extractors import viewpoint_text
from prenatalppkt.etl.extractors import viewpoint_hl7

__all__ = ["observer", "viewpoint_text", "viewpoint_hl7"]
