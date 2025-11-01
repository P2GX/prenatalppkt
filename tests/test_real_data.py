#!/usr/bin/env python3
"""
Quick test with real CUIMC Observer data.

This script is meant to be run directly to test the Observer parser
and integration with real data from CUIMC. It's not a pytest test,
but rather a development/debugging tool.

Usage:
    python tests/test_real_data.py
"""

import logging
from pathlib import Path

from prenatalppkt.parsers.observer_parser import ObserverJSONParser
from prenatalppkt.parsers.observer_integration import (
    ObserverPhenotypicConverter,
    generate_qc_report_summary,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the real data test."""
    # Parse real data
    json_path = Path("data/real/Observer/center/CUIMC/test.json")

    print("=" * 70)  # noqa: T201
    print("TESTING WITH REAL CUIMC DATA")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print()  # noqa: T201

    # Step 1: Parse
    print("Parsing...")  # noqa: T201
    parser = ObserverJSONParser()
    parsed = parser.parse(json_path)

    print("Parsed!")  # noqa: T201
    print(f"   Exam: {parsed.metadata.exam_date.date()}")  # noqa: T201
    print(f"   GA: {parsed.metadata.ga_by_working_edd} weeks")  # noqa: T201
    print(f"   Fetuses: {len(parsed.fetuses)}")  # noqa: T201
    print()  # noqa: T201

    # Step 2: Validate
    print("Validating...")  # noqa: T201
    warnings = parser.validate(parsed)
    if warnings:
        print(f"⚠ {len(warnings)} warnings:")  # noqa: T201
        for w in warnings[:5]:  # Show first 5
            print(f"   • {w}")  # noqa: T201
    else:
        print("✓ All validation passed!")  # noqa: T201
    print()  # noqa: T201

    # Step 3: Convert
    print("Converting to observations...")  # noqa: T201
    converter = ObserverPhenotypicConverter(reference_source="intergrowth")
    observations, qc_report = converter.convert(parsed)

    print(f"✓ Created {len(observations)} observations")  # noqa: T201
    print()  # noqa: T201

    # Show sample observations
    print("Sample observations:")  # noqa: T201
    for obs in observations[:3]:
        status = "✓" if obs.observed else "✗"
        print(  # noqa: T201
            f"  {status} {obs.hpo_label} (percentile: {obs.percentile:.1f}%)"
        )
    print()  # noqa: T201

    # QC Report
    print(generate_qc_report_summary(qc_report))  # noqa: T201
    print()  # noqa: T201

    # Summary
    summary = qc_report.summary()
    if summary["large_discrepancies_count"] > 0:
        print(  # noqa: T201
            f"⚠ ATTENTION: {summary['large_discrepancies_count']} "
            f"large discrepancies found"
        )
        print("   Review QC report above")  # noqa: T201
    else:
        print("✓ All percentiles within acceptable range")  # noqa: T201
    print()  # noqa: T201


if __name__ == "__main__":
    main()
