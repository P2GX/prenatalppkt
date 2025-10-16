"""
phenotypic_export.py

Provides a unified API for converting fetal biometric measurements into
ontology-aware phenotypic observations suitable for Phenopacket export.

This module bridges:
- Quantitative evaluation (percentile bins via FetalGrowthPercentiles)
- Structural measurement classes (SonographicMeasurement subclasses)
- Ontology mapping (TermObservation with HPO terms)
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
        if source not in {"intergrowth", "nichd"}:
            raise ValueError(f"Unsupported source: {source}")

        self.source = source
        self.reference = FetalGrowthPercentiles(source=source)
        mappings_path = mappings_file or DEFAULT_MAPPINGS_FILE
        self.mappings = self._load_mappings(mappings_path)
        self.normal_bins = normal_bins or {"between_10p_50p", "between_50p_90p"}

        logger.info(f"PhenotypicExporter initialized with source={source}")

    def _load_mappings(self, path: Path) -> dict:
        """Load HPO term mappings from YAML configuration file."""
        if not path.exists():
            logger.warning(f"Mappings file not found: {path}. Using empty mappings.")
            return {}

        with open(path, "r") as f:
            raw_mappings = yaml.safe_load(f)

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

        Supports both stepwise (MeasurementResult) and ontology-direct
        (TermObservation) subclasses transparently.
        """
        ga = GestationalAge.from_weeks(gestational_age_weeks)

        # Step 2: Lookup reference thresholds
        try:
            df = self.reference.tables[measurement_type]["ct"]
            row = df.loc[df["Gestational Age (weeks)"].round(1) == round(ga.weeks, 1)]
            if row.empty:
                raise ValueError(
                    f"No reference data for {measurement_type} at GA={ga.weeks}w"
                )
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

        # Step 3: Evaluate (may return MeasurementResult or TermObservation)
        ref_range = ReferenceRange(gestational_age=ga, percentiles=thresholds)
        measurement_result = ref_range.evaluate(value_mm)

        # Step 4: Optional subclass override
        subclass = None
        try:
            from prenatalppkt.measurements import measurement_type_map  # optional

            subclass = measurement_type_map.get(measurement_type)
        except Exception:
            pass

        if subclass is not None:
            instance = subclass()
            res = instance.evaluate(ga, value_mm, ref_range)
            if isinstance(res, TermObservation):
                return res.to_phenotypic_feature()
            measurement_result = res

        # Step 5: Map to ontology
        bin_to_term = self.mappings.get(measurement_type, {})
        normal_bins_to_use = normal_bins or self.normal_bins

        if isinstance(measurement_result, TermObservation):
            term_obs = measurement_result
        else:
            term_obs = TermObservation.from_measurement_result(
                measurement_result=measurement_result,
                bin_to_term=bin_to_term,
                gestational_age=ga,
                normal_bins=normal_bins_to_use,
            )

        # Step 6: Serialize for Phenopacket
        return term_obs.to_phenotypic_feature()

    def batch_export(self, measurements: List[Dict[str, float]]) -> List[dict]:
        """
        Export multiple measurements to phenotypic features.

        Notes
        -----
        We intentionally wrap each iteration in a `try`/`except` block so that
        a single measurement failure does not interrupt batch export. Ruff warns
        about `PERF203` (try/except inside loop), but this is acceptable here
        because robustness is more important than marginal performance.
        """
        results = []
        for meas in measurements:
            try:
                results.append(self.evaluate_and_export(**meas))
            except Exception as e:  # noqa: PERF203 - per-measurement isolation is intentional
                logger.error(f"Failed to export measurement {meas}: {e}")
                results.append({"error": str(e), "measurement": meas})
        return results

    def to_json(self, measurements: List[Dict[str, float]], pretty: bool = True) -> str:
        """Export batch measurements to JSON string."""
        results = self.batch_export(measurements)
        indent = 2 if pretty else None
        return json.dumps(results, indent=indent)
