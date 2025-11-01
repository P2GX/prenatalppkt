"""
observer_pipeline.py

Complete pipeline from Observer JSON to Phenopackets.
"""

import json
import logging
from pathlib import Path
from typing import Dict

from prenatalppkt.parsers.observer_parser import ObserverJSONParser
from prenatalppkt.parsers.observer_integration import ObserverPhenotypicConverter
from prenatalppkt.phenotypic_export import PhenotypicExporter

logger = logging.getLogger(__name__)


class ObserverPipeline:
    """
    Complete pipeline: Observer JSON -> Phenopackets.

    This class orchestrates the entire conversion process from
    Observer ultrasound system JSON exports to GA4GH Phenopackets.

    The pipeline consists of three stages:
    1. Parse: Extract data from Observer JSON
    2. Convert: Transform to TermObservations with HPO terms
    3. Export: Build and write Phenopacket JSON

    Example:
        pipeline = ObserverPipeline(reference_source="intergrowth")
        phenopacket = pipeline.process(
            input_path=Path("exam.json"),
            output_dir=Path("results/")
        )
    """

    def __init__(self, reference_source: str = "intergrowth"):
        """
        Initialize the pipeline.

        Args:
            reference_source: Reference standard to use ("intergrowth" or "nichd")
        """
        self.parser = ObserverJSONParser()
        self.converter = ObserverPhenotypicConverter(reference_source)
        self.exporter = PhenotypicExporter()
        logger.info(f"Initialized pipeline with {reference_source} reference data")

    def process(
        self, input_path: Path, output_dir: Path, validate: bool = True
    ) -> Dict:
        """
        Process an Observer JSON file to Phenopacket.

        Args:
            input_path: Path to Observer JSON file
            output_dir: Directory for output files
            validate: If True, run validation checks on parsed data

        Returns:
            Phenopacket dictionary

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If JSON is malformed or validation fails
        """
        logger.info(f"Processing {input_path}")

        # Stage 1: Parse
        parsed = self.parser.parse(input_path)
        logger.info(
            f"Parsed exam from {parsed.metadata.exam_date.date()} "
            f"with {len(parsed.fetuses)} fetus(es)"
        )

        # Stage 2: Validate
        if validate:
            warnings = self.parser.validate(parsed)
            if warnings:
                logger.warning(f"Validation found {len(warnings)} warnings")
                for w in warnings:
                    logger.warning(f"  - {w}")

        # Stage 3: Convert to observations
        observations, qc_report = self.converter.convert(parsed)
        logger.info(
            f"Converted to {len(observations)} observations "
            f"({qc_report.large_discrepancies_count} QC discrepancies)"
        )

        # Stage 4: Build phenopacket
        for obs in observations:
            self.exporter.add_observation(obs)

        phenopacket = self.exporter.build_phenopacket(
            subject_id=f"FETUS_{parsed.fetuses[0].fetus_number}",
            exam_date=parsed.metadata.exam_date,
        )

        # Stage 5: Write output
        output_path = output_dir / f"phenopacket_{input_path.stem}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(phenopacket, f, indent=2)

        logger.info(f"Wrote phenopacket to {output_path}")

        return phenopacket
