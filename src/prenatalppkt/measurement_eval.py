import logging
import typing
from pathlib import Path

import yaml

from prenatalppkt.measurements.head_circumference_measurement import (
    HeadCircumferenceMeasurement,
)
from prenatalppkt.measurements.term_bin import TermBin
from prenatalppkt.percentile_bin import PercentileRange
from prenatalppkt.sonographic_measurement import SonographicMeasurement
from .biometry_type import BiometryType


logger = logging.getLogger(__name__)

MAPPINGS_DIR = Path(__file__).resolve().parent.parents[1] / "data" / "mappings"
DEFAULT_MAPPINGS_FILE = MAPPINGS_DIR / "biometry2hpo.yaml"


class MeasurementEvaluation:
    def __init__(self) -> None:
        self._mappings = self._load_mappings(DEFAULT_MAPPINGS_FILE)

    # ------------------------------------------------------------------ #
    # Mapping loader
    # ------------------------------------------------------------------ #
    def _load_mappings(
        self, path: Path
    ) -> typing.Dict[BiometryType, SonographicMeasurement]:
        """Load and parse HPO term mappings from YAML."""
        if not path.exists():
            logger.error(f"Mappings file not found: {path}. Using empty mappings.")
            raise FileNotFoundError(
                f"Mappings file not found: {path}. Using empty mappings."
            )

        with open(path, "r") as f:
            raw_mappings = yaml.safe_load(f)

        measurement_d: typing.Dict[BiometryType, SonographicMeasurement] = dict()
        for meas_type, cfg in raw_mappings.items():
            processed: typing.Dict[PercentileRange, TermBin] = dict()
            for k, v in cfg.items():
                prange = PercentileRange.from_string(k)
                processed[prange] = TermBin(
                    termid=v["id"], termlabel=v["label"], normal=v["normal"]
                )
            if meas_type == BiometryType.HEAD_CIRCUMFERENCE:
                sonomsrt: SonographicMeasurement = HeadCircumferenceMeasurement(
                    termbin_d=processed
                )
                measurement_d[meas_type] = sonomsrt
        return measurement_d

    def get_measurement_mapper(
        self, btype: BiometryType
    ) -> SonographicMeasurement | None:
        return self._mappings.get(btype)
