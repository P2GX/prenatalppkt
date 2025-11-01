"""
Observer and ViewPoint parsers for prenatalppkt.

This module provides parsers for ultrasound system data exports:
- Observer JSON parser for biometry and anatomy data
- Integration layer for converting to TermObservations with HPO terms
- QC reporting for data quality validation

Usage:
    from prenatalppkt.parsers import ObserverJSONParser, ObserverPhenotypicConverter

    parser = ObserverJSONParser()
    result = parser.parse(Path("exam.json"))

    converter = ObserverPhenotypicConverter()
    observations, qc_report = converter.convert(result)
"""

from .observer_parser import (
    ObserverJSONParser,
    ObserverParseResult,
    ObserverExamMetadata,
    ObserverMeasurement,
    ObserverFetus,
    ObserverAnatomyFinding,
)

from .observer_integration import (
    ObserverPhenotypicConverter,
    QCReport,
    generate_qc_report_summary,
)

__all__ = [
    # Parser classes and data structures
    "ObserverJSONParser",
    "ObserverParseResult",
    "ObserverExamMetadata",
    "ObserverMeasurement",
    "ObserverFetus",
    "ObserverAnatomyFinding",
    # Integration and QC
    "ObserverPhenotypicConverter",
    "QCReport",
    "generate_qc_report_summary",
]
