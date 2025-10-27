"""
phenotypic_export.py

Unified API for converting fetal biometric measurements into
ontology-aware `TermObservation` objects suitable for Phenopacket export.

Refactor summary (Issue #27)
----------------------------
- Replaced fragile subclass lookup (`measurement_type_map`) with a
robust registry pattern via `SonographicMeasurement`.
- Enforced a consistent return type: `TermObservation` only.
- Split `evaluate_and_export` into:
  * `evaluate_to_observation()` - evaluation + mapping
  * `export_feature()` - serialization to dict
- Improved docstrings, error handling, and separation of concerns.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Dict, Optional, Set, List
import yaml
import json

from prenatalppkt.biometry_type import BiometryType
from prenatalppkt.biometry_reference import FetalGrowthPercentiles
from prenatalppkt.gestational_age import GestationalAge
from prenatalppkt.measurements.reference_range import ReferenceRange
from prenatalppkt.measurements.measurement_result import MeasurementResult
from prenatalppkt.term_observation import TermObservation
from prenatalppkt.sonographic_measurement import SonographicMeasurement
from hpotk import MinimalTerm

logger = logging.getLogger(__name__)

MAPPINGS_DIR = Path(__file__).resolve().parent.parents[1] / "data" / "mappings"
DEFAULT_MAPPINGS_FILE = MAPPINGS_DIR / "biometry_hpo_mappings.yaml"


class PhenotypicExporter:
    """
    High-level interface for phenotype export.

    Responsibilities
    ----------------
    - Evaluate biometric values against gestational-age reference data.
    - Map percentile bins to ontology terms.
    - Return clean, ontology-aware `TermObservation` objects.

    Attributes
    ----------
    source : str
        Reference dataset name ("intergrowth" or "nichd").
    reference : FetalGrowthPercentiles
        Percentile lookup tables.
    mappings : dict
        Measurement-specific ontology configuration.
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

    # ------------------------------------------------------------------ #
    # Mapping loader
    # ------------------------------------------------------------------ #
    def _load_mappings(self, path: Path) -> Dict:
        """Load and parse HPO term mappings from YAML."""
        if not path.exists():
            logger.error(f"Mappings file not found: {path}. Using empty mappings.")
            raise FileNotFoundError(f"Mappings file not found: {path}. Using empty mappings.")

        with open(path, "r") as f:
            raw_mappings = yaml.safe_load(f)

        processed = {}
        for meas_type, cfg in raw_mappings.items():
            bins_cfg = cfg["bins"]
            abnormal_cfg = cfg["abnormal_term"]
            normal_bins = set(cfg.get("normal_bins", []))
            bins: Dict[str, MinimalTerm] = dict()
            for k, v in bins_cfg.items():
                bins[k] = MinimalTerm.create_minimal_term(
                    term_id=v["id"],
                    name=v["label"],
                    alt_term_ids=(),
                    is_obsolete=False,
                )

            abnormal_term = MinimalTerm.create_minimal_term(
                term_id=abnormal_cfg["id"],
                name=abnormal_cfg["label"],
                alt_term_ids=(),
                is_obsolete=False,
            )

            processed[meas_type] = {
                "bins": bins,
                "normal_bins": normal_bins,
                "abnormal_term": abnormal_term,
            }
        return processed
    

    

    # ------------------------------------------------------------------ #
    # Evaluation and export (refactored)
    # ------------------------------------------------------------------ #
    def evaluate_to_observation(
        self,
        measurement_type: BiometryType,
        value_mm: float,
        gestational_age_weeks: float,
        normal_bins: Optional[Set[str]] = None,
    ) -> TermObservation:
        """
        Evaluate a fetal biometric measurement and return a TermObservation.

        Steps:
        1. Retrieve gestational-age-specific thresholds.
        2. Instantiate the registered measurement subclass.
        3. Evaluate the measurement into a `MeasurementResult`.
        4. Map percentile bin to ontology terms using YAML configuration.


        Parameters
        ----------
        measurement_type : BiometryType
            The type of measurement (enum).
        value_mm : float
            The measured value in millimeters.
        gestational_age_weeks : float
            Gestational age in weeks.
        normal_bins : Set[str], optional
            Override default normal bins.

        Returns
        -------
        TermObservation
            The evaluation result with HPO term mapping.
        """
        # Convert enum to string for internal lookups
        measurement_key = measurement_type.value

        ga = GestationalAge.from_weeks(gestational_age_weeks)

        # Step 1: Lookup reference thresholds
        try:
            df = self.reference.tables[measurement_key]["ct"]
            row = df.loc[df["Gestational Age (weeks)"].round(1) == round(ga.weeks, 1)]
            if row.empty:
                raise ValueError(
                    f"No reference data for {measurement_key} at GA={ga.weeks}w"
                )

            percentile_cols = [
                c
                for c in df.columns
                if "percentile" in c.lower() and c != "Gestational Age (weeks)"
            ]
            thresholds: List[float] = row[percentile_cols].iloc[0].astype(float).tolist()
        except KeyError:
            raise ValueError(
                f"Measurement type '{measurement_key}' not available in {self.source} reference"
            )

        # Step 2: Get subclass (strict registry-based polymorphism)
        if measurement_key not in SonographicMeasurement.registry:
            raise KeyError(
                f"Measurement type '{measurement_key}' is not registered. "
                "Ensure a SonographicMeasurement subclass defines it."
            )

        measurement_cls = SonographicMeasurement.registry[measurement_key]
        instance = measurement_cls()

        # Step 3: Evaluate numeric result
        ref_range = ReferenceRange(gestational_age=ga, percentiles=thresholds)
        measurement_result = instance.evaluate(ga, value_mm, ref_range)
        if not isinstance(measurement_result, MeasurementResult):
            raise TypeError(
                f"{measurement_cls.__name__}.evaluate() must return a MeasurementResult"
            )

        # Step 4: Map to ontology
        cfg = self.mappings[measurement_key]
        term_obs = TermObservation.from_measurement_result(
            measurement_result=measurement_result,
            bin_to_term=cfg["bins"],
            gestational_age=ga,
            normal_bins=normal_bins or cfg["normal_bins"],
            abnormal_term=cfg["abnormal_term"],
        )
        return term_obs

    # ------------------------------------------------------------------ #
    # Wrapper for serialization
    # ------------------------------------------------------------------ #
    def export_feature(
        self,
        measurement_type: BiometryType,
        value_mm: float,
        gestational_age_weeks: float,
        **kwargs,
    ) -> dict:
        """Serialize a TermObservation as a Phenopacket-style dictionary."""
        obs = self.evaluate_to_observation(
            measurement_type, value_mm, gestational_age_weeks, **kwargs
        )
        return obs.to_phenotypic_feature()

    def batch_export(self, measurements: List[Dict[str, float]]) -> List[dict]:
        """Export multiple measurements to Phenopacket-style features."""
        results = []
        for meas in measurements:
            try:
                results.append(self.export_feature(**meas))
            except Exception as e:  # noqa: PERF203 - intentional isolation for per-measurement robustness
                logger.error(f"Failed to export measurement {meas}: {e}")
                results.append({"error": str(e), "measurement": meas})
        return results

    def to_json(self, measurements: List[Dict[str, float]], pretty: bool = True) -> str:
        """Export batch measurements to JSON string."""
        results = self.batch_export(measurements)
        indent = 2 if pretty else None
        return json.dumps(results, indent=indent)
