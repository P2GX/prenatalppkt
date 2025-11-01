"""
observer_parser.py

Parser for Observer ultrasound system JSON exports.
Extracts fetal biometry measurements, anatomy findings, and exam metadata.

Usage:
    parser = ObserverJSONParser()
    result = parser.parse(Path("exam_data.json"))

    print(f"GA: {result.metadata.ga_by_working_edd} weeks")
    for fetus in result.fetuses:
        for meas in fetus.measurements:
            print(f"{meas.label}: {meas.value_mm}mm")
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


logger = logging.getLogger(__name__)


@dataclass
class ObserverExamMetadata:
    """
    Metadata from Observer exam.

    Attributes:
        exam_date: Date of ultrasound examination
        site_name: Name of examination site/facility
        fetus_count: Number of fetuses
        ga_by_working_edd: Gestational age in weeks (ultrasound-based, most reliable)
        lmp_date: Last menstrual period date (optional)
        ga_by_dates: GA calculated from LMP (optional, less reliable)
        icd10_codes: List of ICD-10 diagnostic codes
        referring_physician: Name of referring physician
        accession_id: Exam accession ID
        exam_locator: Exam locator/identifier
    """

    exam_date: datetime
    site_name: str
    fetus_count: int
    ga_by_working_edd: float  # weeks (ultrasound-based, most reliable)
    lmp_date: Optional[datetime] = None
    ga_by_dates: Optional[float] = None  # weeks (LMP-based, less reliable)
    icd10_codes: List[str] = field(default_factory=list)
    referring_physician: Optional[str] = None
    accession_id: Optional[str] = None
    exam_locator: Optional[str] = None


@dataclass
class ObserverMeasurement:
    """
    Single biometry measurement from Observer.

    Implements dual percentile strategy: stores both Observer's reported
    percentile (which we trust) and our recalculated percentile (for QC).

    Attributes:
        label: Measurement label (e.g., "AC", "BPD", "HC", "Femur")
        value_mm: Measurement value converted to millimeters
        unit: Original unit from JSON
        fetus_number: Which fetus this measurement belongs to
        percentile_source: Observer's reported percentile (TRUST THIS)
        percentile_recalculated: Our recalculated value (for QC)
        calculated_ega: GA estimated by this measurement
    """

    label: str
    value_mm: float
    unit: str
    fetus_number: int
    percentile_source: Optional[float]
    percentile_recalculated: Optional[float] = None
    calculated_ega: Optional[float] = None

    def percentile_discrepancy(self) -> Optional[float]:
        """
        Calculate percentage difference between source and recalculated.

        Returns:
            Absolute difference between percentiles, or None if either is missing
        """
        if self.percentile_source is None or self.percentile_recalculated is None:
            return None
        return abs(self.percentile_source - self.percentile_recalculated)


@dataclass
class ObserverAnatomyFinding:
    """
    Anatomy finding from Observer.

    Attributes:
        structure: Anatomical structure (e.g., "Head", "Heart", "Face/Neck")
        state: Finding state ("Normal", "Abnormal", "Unseen")
        fetus_number: Which fetus this finding belongs to
        anomalies: List of free-text anomaly descriptions
        detail_findings: List of sub-structure details with labels and states
    """

    structure: str
    state: str
    fetus_number: int
    anomalies: List[str] = field(default_factory=list)
    detail_findings: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ObserverFetus:
    """
    Data for a single fetus.

    Attributes:
        fetus_number: Fetus identifier (1, 2, etc.)
        measurements: List of biometry measurements
        anatomy: List of anatomy findings
        heart_rate: Fetal heart rate in bpm
        presentation: Fetal presentation (e.g., "Vertex", "Breech")
        ga_by_sonography: GA calculated for this fetus
    """

    fetus_number: int
    measurements: List[ObserverMeasurement] = field(default_factory=list)
    anatomy: List[ObserverAnatomyFinding] = field(default_factory=list)
    heart_rate: Optional[float] = None
    presentation: Optional[str] = None
    ga_by_sonography: Optional[int] = None


@dataclass
class ObserverParseResult:
    """
    Result of parsing an Observer JSON file.

    Attributes:
        metadata: Exam-level metadata
        fetuses: List of fetus data
        raw_json: Original JSON for debugging/provenance
        parse_warnings: List of warnings generated during parsing
    """

    metadata: ObserverExamMetadata
    fetuses: List[ObserverFetus]
    raw_json: dict
    parse_warnings: List[str] = field(default_factory=list)

    def has_warnings(self) -> bool:
        """
        Check if any warnings were generated during parsing.

        Returns:
            True if warnings exist, False otherwise
        """
        return len(self.parse_warnings) > 0


class ObserverJSONParser:
    """
    Parser for Observer ultrasound system JSON exports.

    Features:
    - Extracts biometry measurements (AC, BPD, HC, FL, OFD)
    - Converts units (cm -> mm)
    - Dual percentile tracking (source + recalculated)
    - Anatomy findings and anomalies
    - Multi-fetus support
    - Validation and QC warnings

    Example:
        parser = ObserverJSONParser()
        result = parser.parse(Path("exam_data.json"))

        if result.has_warnings():
            for warning in result.parse_warnings:
                print(f"{warning}")

        for fetus in result.fetuses:
            for meas in fetus.measurements:
                print(f"{meas.label}: {meas.value_mm}mm")
    """

    # Measurement label mapping
    MEASUREMENT_MAP = {
        "AC": "abdominal_circumference",
        "BPD": "biparietal_diameter",
        "HC": "head_circumference",
        "Femur": "femur_length",
        # Additional measurements (not yet in YAML)
        "Cerebellum": "cerebellum",
        "Nuchal Fold": "nuchal_fold",
    }

    # Biological plausibility ranges (mm)
    PLAUSIBILITY_RANGES = {
        "AC": (50, 500),
        "BPD": (10, 120),
        "HC": (50, 500),
        "Femur": (10, 100),
        "Cerebellum": (5, 80),
        "Nuchal Fold": (1, 20),
    }

    def parse(self, json_path: Path) -> ObserverParseResult:
        """
        Parse an Observer JSON file.

        Args:
            json_path: Path to Observer JSON file

        Returns:
            ObserverParseResult containing extracted data

        Raises:
            ValueError: If JSON is malformed or required fields missing
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        if not json_path.exists():
            raise FileNotFoundError(f"File not found: {json_path}")

        logger.info(f"Parsing Observer JSON: {json_path}")

        # Load JSON
        try:
            with open(json_path, encoding="utf-8") as f:
                raw_json = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}") from e

        parse_warnings = []

        # Parse exam metadata
        if "exam" not in raw_json:
            raise ValueError("Missing required 'exam' section in JSON")

        try:
            metadata = self._parse_exam_metadata(raw_json["exam"])
        except KeyError as e:
            raise ValueError(f"Missing required exam field: {e}") from e

        # Parse fetuses
        if "fetuses" not in raw_json or not raw_json["fetuses"]:
            raise ValueError("Missing or empty 'fetuses' array in JSON")

        fetuses = []
        for fetus_data in raw_json["fetuses"]:
            try:
                fetus = self._parse_fetus(fetus_data)
                fetuses.append(fetus)
            except Exception as e:
                warning = f"Error parsing fetus data: {e}"
                logger.warning(warning)
                parse_warnings.append(warning)

        if not fetuses:
            raise ValueError("No fetuses could be parsed from JSON")

        result = ObserverParseResult(
            metadata=metadata,
            fetuses=fetuses,
            raw_json=raw_json,
            parse_warnings=parse_warnings,
        )

        logger.info(f"Successfully parsed {len(fetuses)} fetus(es)")

        return result

    def _parse_exam_metadata(self, exam_data: dict) -> ObserverExamMetadata:
        """
        Extract exam-level metadata.

        Args:
            exam_data: Exam section from Observer JSON

        Returns:
            ObserverExamMetadata object

        Raises:
            ValueError: If required fields are missing
        """
        # Parse exam date (required)
        exam_date_str = exam_data.get("exm_date")
        if not exam_date_str:
            raise ValueError("Missing required field: exm_date")
        exam_date = datetime.fromisoformat(exam_date_str)

        # Parse LMP date (optional, may be placeholder)
        lmp_date = None
        lmp_str = exam_data.get("lmp")
        if lmp_str and lmp_str != "0001-01-01":
            try:
                lmp_date = datetime.fromisoformat(lmp_str)
            except ValueError:
                logger.warning(f"Invalid LMP date: {lmp_str}")

        # Extract ICD-10 codes
        icd10_codes = []
        if "examIcd10Indication" in exam_data and exam_data["examIcd10Indication"]:
            for indication in exam_data["examIcd10Indication"]:
                if "code" in indication:
                    icd10_codes.append(indication["code"])

        # Extract referring physician
        referring_physician = None
        if "examReferring" in exam_data and exam_data["examReferring"]:
            # Take first referring physician
            if exam_data["examReferring"] and "name" in exam_data["examReferring"][0]:
                referring_physician = exam_data["examReferring"][0]["name"]

        return ObserverExamMetadata(
            exam_date=exam_date,
            site_name=exam_data.get("site_name", "Unknown"),
            fetus_count=exam_data.get("fetus_count", 0),
            ga_by_working_edd=exam_data.get("ga_by_working_edd", 0),
            lmp_date=lmp_date,
            ga_by_dates=exam_data.get("ga_by_dates") or None,
            icd10_codes=icd10_codes,
            referring_physician=referring_physician,
            accession_id=exam_data.get("accession_id"),
            exam_locator=exam_data.get("exm_locator"),
        )

    def _parse_fetus(self, fetus_data: dict) -> ObserverFetus:
        """
        Extract data for a single fetus.

        Args:
            fetus_data: Fetus section from Observer JSON

        Returns:
            ObserverFetus object with measurements and anatomy
        """
        # Get fetus metadata
        fetus_info = fetus_data.get("fetus", {})
        fetus_number = fetus_info.get("fetus_number", 1)

        # Parse measurements
        measurements = []
        if "measurements" in fetus_data and fetus_data["measurements"]:
            measurements = self._parse_measurements(
                fetus_data["measurements"], fetus_number
            )

        # Parse anatomy
        anatomy = []
        if "anatomy" in fetus_data and fetus_data["anatomy"]:
            anatomy = self._parse_anatomy(fetus_data["anatomy"], fetus_number)

        return ObserverFetus(
            fetus_number=fetus_number,
            measurements=measurements,
            anatomy=anatomy,
            heart_rate=fetus_info.get("heart_bpm"),
            presentation=fetus_info.get("fetus_presentation"),
            ga_by_sonography=fetus_info.get("ga_by_sonography"),
        )

    def _parse_measurements(
        self, measurements: List[dict], fetus_number: int
    ) -> List[ObserverMeasurement]:
        """
        Extract and normalize measurements.

        Args:
            measurements: List of measurement dictionaries from JSON
            fetus_number: Which fetus these measurements belong to

        Returns:
            List of ObserverMeasurement objects
        """
        parsed_measurements = []

        for meas_data in measurements:
            try:
                label = meas_data.get("label")
                if not label:
                    logger.warning(f"Measurement missing label, skipping: {meas_data}")
                    continue

                value = meas_data.get("value")
                if value is None:
                    logger.warning(f"Measurement {label} missing value, skipping")
                    continue

                unit = meas_data.get("unit_of_measure", "cm")

                # Convert to mm
                value_mm = self._convert_to_mm(value, unit)

                # Get Observer's reported percentile (TRUST THIS)
                percentile_source = meas_data.get("calculated_percentile")

                measurement = ObserverMeasurement(
                    label=label,
                    value_mm=value_mm,
                    unit=unit,
                    fetus_number=fetus_number,
                    percentile_source=percentile_source,
                    calculated_ega=meas_data.get("calculated_ega"),
                )

                parsed_measurements.append(measurement)

            except Exception as e:
                logger.warning(f"Error parsing measurement: {e}")
                continue

        return parsed_measurements

    def _parse_anatomy(
        self, anatomy: List[dict], fetus_number: int
    ) -> List[ObserverAnatomyFinding]:
        """
        Extract anatomy findings.

        Args:
            anatomy: List of anatomy dictionaries from JSON
            fetus_number: Which fetus these findings belong to

        Returns:
            List of ObserverAnatomyFinding objects
        """
        findings = []

        for anat_data in anatomy:
            try:
                main = anat_data.get("main", {})
                structure = main.get("label")
                state = main.get("anat_state", "Unseen")

                if not structure:
                    continue

                # Extract anomalies (free-text descriptions)
                anomalies = []
                if "anomalies" in anat_data and anat_data["anomalies"]:
                    for anomaly in anat_data["anomalies"]:
                        if "description" in anomaly:
                            anomalies.append(anomaly["description"])

                # Extract detail findings (sub-structures)
                detail_findings = []
                if "detail" in anat_data and anat_data["detail"]:
                    for detail in anat_data["detail"]:
                        detail_findings.append(
                            {
                                "label": detail.get("label", ""),
                                "state": detail.get("anat_det_state", "Unseen"),
                            }
                        )

                finding = ObserverAnatomyFinding(
                    structure=structure,
                    state=state,
                    fetus_number=fetus_number,
                    anomalies=anomalies,
                    detail_findings=detail_findings,
                )

                findings.append(finding)

            except Exception as e:
                logger.warning(f"Error parsing anatomy finding: {e}")
                continue

        return findings

    def _convert_to_mm(self, value: float, unit: str) -> float:
        """
        Convert measurement to millimeters.

        Args:
            value: Measurement value
            unit: Unit of measurement ("cm" or "mm")

        Returns:
            Value converted to millimeters
        """
        unit_lower = unit.lower()

        if unit_lower == "cm":
            return value * 10
        elif unit_lower == "mm":
            return value
        else:
            logger.warning(f"Unknown unit '{unit}', assuming mm")
            return value

    def validate(self, result: ObserverParseResult) -> List[str]:
        """
        Validate parsed data for completeness and plausibility.

        Checks:
        - Required measurements present
        - Biological plausibility ranges
        - GA consistency
        - Multi-fetus data consistency

        Args:
            result: Parsed Observer data to validate

        Returns:
            List of validation warnings (empty if all valid)
        """
        warnings = []

        # Check GA range
        ga = result.metadata.ga_by_working_edd
        if ga < 10 or ga > 42:
            warnings.append(f"GA {ga:.1f} weeks outside expected range [10-42 weeks]")

        # Check each fetus
        for fetus in result.fetuses:
            fetus_id = f"Fetus {fetus.fetus_number}"

            # Check required measurements present
            labels = {m.label for m in fetus.measurements}
            required = {"AC", "BPD", "HC", "Femur"}
            missing = required - labels
            if missing:
                warnings.append(f"{fetus_id}: Missing required measurements {missing}")

            # Check biological plausibility
            for meas in fetus.measurements:
                if meas.label in self.PLAUSIBILITY_RANGES:
                    min_val, max_val = self.PLAUSIBILITY_RANGES[meas.label]
                    if not (min_val <= meas.value_mm <= max_val):
                        warnings.append(
                            f"{fetus_id}: {meas.label} value {meas.value_mm:.1f}mm "
                            f"outside plausible range [{min_val}-{max_val}mm]"
                        )

            # Check for heart rate
            if fetus.heart_rate is None:
                warnings.append(f"{fetus_id}: No heart rate recorded")
            elif not (100 <= fetus.heart_rate <= 200):
                warnings.append(
                    f"{fetus_id}: Heart rate {fetus.heart_rate} bpm "
                    f"outside typical range [100-200 bpm]"
                )

        # Check fetus count consistency
        expected_count = result.metadata.fetus_count
        actual_count = len(result.fetuses)
        if expected_count != actual_count:
            warnings.append(
                f"Fetus count mismatch: metadata says {expected_count}, "
                f"but found {actual_count} fetuses"
            )

        return warnings
