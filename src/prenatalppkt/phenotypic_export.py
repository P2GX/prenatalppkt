"""
phenotypic_export.py

Provides a unified API for converting fetal biometric measurements into
ontology-aware phenotypic observations suitable for Phenopacket export.

This module bridges:
- Quantitative evaluation (percentile bins via FetalGrowthPercentiles)
- Structural measurement classes (SonographicMeasurement subclasses)
- Ontology mapping (TermObservation with HPO terms)

Example Usage
-------------
exporter = PhenotypicExporter(source="intergrowth")
result = exporter.evaluate_and_export(measurement_type="head_circumference", value_mm=175.0, gestational_age_weeks=20.86)
print(result)
{
    "type": {"id": "HP:0000252", "label": "Microcephaly"},
    "excluded": False,
    "description": "Measurement at 20w6d gestation"
}
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Dict, Optional, Set, List
import yaml
import json

from prenatalppkt.biometry_reference import FetalGrowthPercentiles
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.term_observation import TermObservation
from hpotk import MinimalTerm

logger = logging.getLogger(__name__)

# Default mappings file location
MAPPINGS_DIR = Path(__file__).resolve().parent.parents[1] / "data" / "mappings"
DEFAULT_MAPPINGS_FILE = MAPPINGS_DIR / "biometry_hpo_mappings.yaml"


class PhenotypicExporter:
    """
    Unified exporter for fetal biometric measurements to phenotypic observations.

    Responsibilities
    ----------------
    1. Load percentile reference data (INTERGROWTH or NIHCD)
    2. Evaluate raw measurements against percentile thresholds
    3. Map percentile bins to HPO terms via configurable mappings
    4. Export results as Phenopacket-compatible dictionaries

    Attributes
    ----------
    source : str
        Reference data source ("intergrowth" or "nichd")
    reference : FetalGrowthPercentiles
        Loaded percentile reference tables
    mappings : dict
        HPO term mappings for each measurement type
    normal_bins : set[str]
        Default percentile bins considered "normal"
    """

    def __init__(
        self,
        source: str = "intergrowth",
        mappings_file: Optional[Path] = None,
        normal_bins: Optional[Set[str]] = None,
    ):
        """
        Initialize the phenotypic exporter.

        Parameters
        ----------
        source : str
            Reference data source: "intergrowth" or "nichd"
        mappings_file : Path, optional
            Path to custom HPO mappings YAML file
        normal_bins : set[str], optional
            Custom definition of normal percentile bins.
            Defaults to {"between_10p_50p", "between_50p_90p"}
        """
        if source not in {"intergrowth", "nichd"}:
            raise ValueError(f"Unsupported source: {source}")

        self.source = source
        self.reference = FetalGrowthPercentiles(source=source)

        # Load HPO term mappings
        mappings_path = mappings_file or DEFAULT_MAPPINGS_FILE
        self.mappings = self._load_mappings(mappings_path)

        # Default normal range: 10th-90th percentile
        self.normal_bins = normal_bins or {"between_10p_50p", "between_50p_90p"}

        logger.info(f"PhenotypicExporter initialized with source={source}")

    def _load_mappings(self, path: Path) -> dict:
        """
        Load HPO term mappings from YAML configuration file.

        Expected format:
        ```yaml
        head_circumference:
          below_3p: {id: "HP:0000252", label: "Microcephaly"}
          between_3p_5p: {id: "HP:0000252", label: "Microcephaly"}
          ...
        ```

        Returns
        -------
        dict
            Nested mapping: measurement_type -> bin_key -> HPO term dict
        """
        if not path.exists():
            logger.warning(f"Mappings file not found: {path}. Using empty mappings.")
            return {}

        with open(path, "r") as f:
            raw_mappings = yaml.safe_load(f)

        # Convert dict format to MinimalTerm objects
        processed = {}
        for meas_type, bin_mappings in raw_mappings.items():
            processed[meas_type] = {}
            for bin_key, term_dict in (bin_mappings or {}).items():
                if not term_dict:
                    processed[meas_type][bin_key] = None
                    continue

                processed[meas_type][bin_key] = MinimalTerm.create_minimal_term(
                    term_id=term_dict["id"],
                    name=term_dict["label"],
                    alt_term_ids=(),
                    is_obsolete=False,
                )
        return processed

    def evaluate_and_export(
        self,
        measurement_type: str,
        value_mm: float,
        gestational_age_weeks: float,
        population: Optional[str] = None,
        normal_bins: Optional[Set[str]] = None,
    ) -> dict:
        """
        Evaluate a fetal biometric measurement and export as Phenopacket-style dict.

        Parameters
        ----------
        measurement_type : str
            Type of measurement (e.g., "head_circumference", "femur_length")
        value_mm : float
            Measured value in millimeters
        gestational_age_weeks : float
            Gestational age (can be fractional, e.g., 20.86)
        population : str, optional
            Population identifier for NIHCD stratification (future use)
        normal_bins : set[str], optional
            Override default normal bins for this evaluation

        Returns
        -------
        dict
            Phenopacket-compatible dictionary with type, excluded flag, description

        Raises
        ------
        ValueError
            If measurement_type is unsupported or reference data unavailable
        """
        # Step 1: Convert gestational age to structured format
        ga = GestationalAge.from_weeks(gestational_age_weeks)

        # Step 2: Lookup percentile thresholds for this GA
        try:
            # Get the full row of reference data for this GA
            df = self.reference.tables[measurement_type]["ct"]
            row = df.loc[df["Gestational Age (weeks)"].round(1) == round(ga.weeks, 1)]

            if row.empty:
                raise ValueError(
                    f"No reference data for {measurement_type} at GA={ga.weeks}w"
                )

            # Extract percentile columns (3rd through 97th)
            percentile_cols = [
                c
                for c in df.columns
                if "percentile" in c.lower() and c != "Gestational Age (weeks)"
            ]
            thresholds = row[percentile_cols].iloc[0].astype(float).tolist()

        except KeyError:
            raise ValueError(
                f"Measurement type '{measurement_type}' not available in {self.source} reference"
            )

        # Step 3: Create ReferenceRange and evaluate measurement
        ref_range = ReferenceRange(gestational_age=ga, percentiles=thresholds)
        measurement_result = ref_range.evaluate(value_mm)

        # Step 4: Get HPO term mapping for this measurement type
        """
        bin_to_term = {
            k: (
                MinimalTerm.create_minimal_term(
                    term_id=v["id"], name=v["label"], alt_term_ids=(), is_obsolete=False
                )
                if isinstance(v, dict)
                else v
            )
            for k, v in self.mappings.get(measurement_type, {}).items()
        }
        # Ensure all mappings are MinimalTerm instances, not dicts
        for k, term in bin_to_term.items():
            if isinstance(term, dict):
                bin_to_term[k] = MinimalTerm.create_minimal_term(
                    term_id=term["id"],
                    name=term["label"],
                    alt_term_ids=(),
                    is_obsolete=False,
                )
        """
        bin_to_term = self.mappings.get(measurement_type, {})

        # Step 5: Convert to TermObservation
        normal_bins_to_use = normal_bins or self.normal_bins
        term_obs = TermObservation.from_measurement_result(
            measurement_result=measurement_result,
            bin_to_term=bin_to_term,
            gestational_age=ga,
            normal_bins=normal_bins_to_use,
        )

        # Step 6: Export to Phenopacket-style dictionary
        return term_obs.to_phenotypic_feature()

    def batch_export(self, measurements: List[Dict[str, float]]) -> List[dict]:
        """
        Export multiple measurements to phenotypic features.

        Parameters
        ----------
        measurements : list of dict
            Each dict must contain:
            - measurement_type: str
            - value_mm: float
            - gestational_age_weeks: float

        Returns
        -------
        list of dict
            List of Phenopacket-style feature dictionaries
        """
        results = []
        for meas in measurements:
            result = None
            try:
                result = self.evaluate_and_export(**meas)
            except Exception as e:
                logger.error(f"Failed to export measurement {meas}: {e}")
                result = {"error": str(e), "measurement": meas}
            results.append(result)
        return results

    def to_json(self, measurements: List[Dict[str, float]], pretty: bool = True) -> str:
        """
        Export batch measurements to JSON string.

        Parameters
        ----------
        measurements : list of dict
            Measurements to export (see batch_export)
        pretty : bool
            Whether to format JSON with indentation

        Returns
        -------
        str
            JSON string representation
        """
        results = self.batch_export(measurements)
        indent = 2 if pretty else None
        return json.dumps(results, indent=indent)
