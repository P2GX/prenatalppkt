"""
observer_integration.py

Integrates Observer parsed data with prenatalppkt measurement evaluation.
Implements dual percentile strategy: trust Observer's percentile but recalculate for QC.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging

from prenatalppkt.parsers.observer_parser import (
    ObserverParseResult,
)
from prenatalppkt.measurement_eval import MeasurementEvaluation
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.term_observation import TermObservation
from prenatalppkt.biometry_reference import FetalGrowthPercentiles

logger = logging.getLogger(__name__)


@dataclass
class QCReport:
    """
    Quality control report for Observer data conversion.

    Tracks discrepancies between Observer-reported percentiles
    and recalculated percentiles from reference data.
    """

    measurement_count: int = 0
    large_discrepancies_count: int = 0
    discrepancies: List[Dict[str, Any]] = field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        """
        Return summary statistics for the QC report.

        Returns:
            Dictionary with measurement_count and large_discrepancies_count
        """
        return {
            "measurement_count": self.measurement_count,
            "large_discrepancies_count": self.large_discrepancies_count,
        }


def generate_qc_report_summary(qc_report: QCReport) -> str:
    """
    Generate human-readable QC report summary.

    Args:
        qc_report: QC report to summarize

    Returns:
        Formatted string summary of the QC report
    """
    lines = []
    lines.append("=" * 70)
    lines.append("QC REPORT")
    lines.append("=" * 70)
    lines.append(f"Total measurements: {qc_report.measurement_count}")
    lines.append(f"Large discrepancies: {qc_report.large_discrepancies_count}")

    if qc_report.discrepancies:
        lines.append("\nDiscrepancies (showing first 5):")
        for disc in qc_report.discrepancies[:5]:
            label = disc.get("label", "Unknown")
            fetus = disc.get("fetus", 1)
            source = disc.get("source", 0)
            recalc = disc.get("recalculated", 0)
            diff = disc.get("discrepancy", 0)
            lines.append(
                f"  - Fetus {fetus}, {label}: "
                f"Observer={source:.1f}%, Recalc={recalc:.1f}% "
                f"(diff={diff:.1f}%)"
            )

    return "\n".join(lines)


class ObserverPhenotypicConverter:
    """
    Converts Observer parsed data to TermObservations.

    This converter takes parsed Observer JSON data and converts biometry
    measurements into TermObservation objects with HPO term mappings.
    It also performs quality control by comparing Observer-reported
    percentiles with recalculated values from reference data.

    Example:
        parser = ObserverJSONParser()
        parsed = parser.parse(Path("exam.json"))

        converter = ObserverPhenotypicConverter(reference_source="intergrowth")
        observations, qc_report = converter.convert(parsed)

        # observations is List[TermObservation] ready for Phenopacket export
        # qc_report contains quality control metrics
    """

    def __init__(self, reference_source: str = "intergrowth"):
        """
        Initialize the converter with reference data source.

        Args:
            reference_source: Reference standard to use ("intergrowth" or "nichd")
        """
        self.factory = MeasurementEvaluation()
        self.ref_data = FetalGrowthPercentiles(source=reference_source)
        logger.info(f"Initialized converter with {reference_source} reference data")

    def convert(
        self, parsed: ObserverParseResult
    ) -> Tuple[List[TermObservation], QCReport]:
        """
        Convert parsed Observer data to TermObservations.

        Args:
            parsed: Result from ObserverJSONParser

        Returns:
            Tuple of (observations, qc_report) where observations is a list
            of TermObservation objects and qc_report contains QC metrics
        """
        observations = []
        qc_report = QCReport()

        # Calculate gestational age
        ga = GestationalAge.from_weeks(parsed.metadata.ga_by_working_edd)
        logger.info(
            f"Converting measurements at GA {parsed.metadata.ga_by_working_edd} weeks"
        )

        for fetus in parsed.fetuses:
            logger.debug(f"Processing fetus {fetus.fetus_number}")

            for measurement in fetus.measurements:
                # Map Observer label to prenatalppkt measurement type
                meas_type = self._map_measurement_type(measurement.label)
                if meas_type is None:
                    logger.debug(
                        f"Skipping unsupported measurement: {measurement.label}"
                    )
                    continue  # Skip unsupported measurements

                qc_report.measurement_count += 1

                # Calculate percentile using reference data
                percentile = self.ref_data.calculate_percentile(
                    measurement_type=meas_type,
                    gestational_age_weeks=parsed.metadata.ga_by_working_edd,
                    value_mm=measurement.value_mm,
                )

                # Store recalculated percentile for QC comparison
                measurement.percentile_recalculated = percentile

                # Check for large discrepancies between Observer and recalculated
                if measurement.percentile_source is not None:
                    discrepancy = abs(percentile - measurement.percentile_source)
                    if discrepancy > 10:  # More than 10 percentile points difference
                        qc_report.large_discrepancies_count += 1
                        qc_report.discrepancies.append(
                            {
                                "label": measurement.label,
                                "fetus": fetus.fetus_number,
                                "source": measurement.percentile_source,
                                "recalculated": percentile,
                                "discrepancy": discrepancy,
                            }
                        )
                        logger.warning(
                            f"Large discrepancy for {measurement.label}: "
                            f"Observer={measurement.percentile_source:.1f}%, "
                            f"Recalc={percentile:.1f}%"
                        )

                # Get mapper and create observation
                mapper = self.factory.get_measurement_mapper(meas_type)
                if mapper is None:
                    raise ValueError(f"No mapper for measurement type: {meas_type}")

                # Use recalculated percentile for HPO term assignment
                obs = mapper.from_percentile(percentile, ga)

                # Add fetus context (for multi-fetus cases)
                obs.fetus_number = fetus.fetus_number

                observations.append(obs)

        logger.info(
            f"Created {len(observations)} observations from "
            f"{qc_report.measurement_count} measurements"
        )

        return observations, qc_report

    def _map_measurement_type(self, observer_label: str) -> Optional[str]:
        """
        Map Observer measurement labels to prenatalppkt types.

        Args:
            observer_label: Label from Observer JSON (e.g., "AC", "BPD", "HC")

        Returns:
            Internal measurement type name or None if not supported
        """
        mapping = {
            "AC": "abdominal_circumference",
            "BPD": "biparietal_diameter",
            "HC": "head_circumference",
            "Femur": "femur_length",
        }
        return mapping.get(observer_label)

    def convert_anatomy_to_observations(
        self, parsed: ObserverParseResult
    ) -> List[TermObservation]:
        """
        Convert anatomy findings to TermObservations.

        Note: This is more complex as it requires mapping free-text
        anatomy descriptions to HPO terms. Initial implementation may
        just log these for manual review.

        Args:
            parsed: Result from ObserverJSONParser

        Returns:
            List of TermObservations from anatomy findings

        TODO:
            Implement anatomy-to-HPO mapping. This requires either:
            1. A lookup table for common anatomy findings
            2. NLP-based mapping
            3. Manual curation workflow
        """
        logger.warning("Anatomy-to-HPO mapping not yet implemented")
        return []
