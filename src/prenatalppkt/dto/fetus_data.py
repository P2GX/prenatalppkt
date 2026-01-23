"""
src/prenatalppkt/dto/fetus_data.py

Top-level Data Transfer Object for a single fetus entry in the Observer JSON.
This class acts as a container for semantically-grouped sub-components parsed
from the 'fetuses' array.
"""

from typing import Optional
from .observer.fetuses.fetus_core_data import FetusCoreData
from .observer.builders.fetus_anatomy_data import FetusAnatomyData
from .observer.builders.fetus_biometry_data import FetusBiometryData
from .observer.builders.fetus_echo_data import FetusEchoData
from .observer.builders.fetus_procedures_data import FetusProceduresData
from .observer.builders.fetus_environment_data import FetusEnvironmentData
from .observer.builders.fetus_gestational_data import FetusGestationalData


class FetusData:
    """
    Data transfer object for fetal phenotype and attributes.

    This class aggregates semantically-grouped Observer JSON data into 7 logical
    categories instead of 21 individual fields, making construction more intuitive
    and maintainable.

    Attributes:
        fetus_core: Core fetal metadata (fetus number, GA, gender, presentation)
        anatomy: Anatomy findings, impressions, and HPO terms
        biometry: Measurements, ratios, and estimated fetal weights
        echo: Fetal echocardiography data
        procedures: Prenatal procedures and assessments
        environment: Fetal environment (fluids, vessels, placenta)
        gestational: Early pregnancy and gestational data
    """

    def __init__(
        self,
        fetus_core: FetusCoreData,
        anatomy: Optional[FetusAnatomyData] = None,
        biometry: Optional[FetusBiometryData] = None,
        echo: Optional[FetusEchoData] = None,
        procedures: Optional[FetusProceduresData] = None,
        environment: Optional[FetusEnvironmentData] = None,
        gestational: Optional[FetusGestationalData] = None,
    ) -> None:
        """
        Encapsulates phenotype and biometric data for one fetus.

        Args:
            fetus_core: Required core fetal metadata
            anatomy: Optional anatomy findings and impressions
            biometry: Optional biometric measurements
            echo: Optional fetal echocardiography data
            procedures: Optional prenatal procedures
            environment: Optional fetal environment data
            gestational: Optional early pregnancy data
        """
        self._fetus_core = fetus_core
        self._anatomy = anatomy
        self._biometry = biometry
        self._echo = echo
        self._procedures = procedures
        self._environment = environment
        self._gestational = gestational

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def fetus_core(self) -> FetusCoreData:
        """Core fetal attributes (fetus number, GA, gender, etc.)."""
        return self._fetus_core

    @property
    def anatomy(self) -> Optional[FetusAnatomyData]:
        """Anatomy findings, impressions, and HPO terms."""
        return self._anatomy

    @property
    def biometry(self) -> Optional[FetusBiometryData]:
        """Biometric measurements, ratios, and EFWs."""
        return self._biometry

    @property
    def echo(self) -> Optional[FetusEchoData]:
        """Fetal echocardiography data."""
        return self._echo

    @property
    def procedures(self) -> Optional[FetusProceduresData]:
        """Prenatal procedures and assessments."""
        return self._procedures

    @property
    def environment(self) -> Optional[FetusEnvironmentData]:
        """Fetal environment (fluids, vessels, placenta)."""
        return self._environment

    @property
    def gestational(self) -> Optional[FetusGestationalData]:
        """Early pregnancy and gestational data."""
        return self._gestational

    # -------------------------------------------------------------------------
    # Convenience Properties for Common Access Patterns
    # -------------------------------------------------------------------------

    @property
    def hpo_terms(self):
        """Convenience accessor for HPO terms from anatomy data."""
        return self._anatomy.hpo_terms if self._anatomy else []

    @property
    def measurements(self):
        """Convenience accessor for measurements from biometry data."""
        return self._biometry.measurements if self._biometry else None

    @property
    def ratios(self):
        """Convenience accessor for ratios from biometry data."""
        return self._biometry.ratios if self._biometry else None

    @property
    def efws(self):
        """Convenience accessor for EFWs from biometry data."""
        return self._biometry.efws if self._biometry else None

    @property
    def fetus_number(self):
        """Convenience accessor for fetus number from core data."""
        return self._fetus_core.fetus_number if self._fetus_core else None

    # -------------------------------------------------------------------------
    # Representation
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"FetusData("
            f"fetus_core={self._fetus_core}, "
            f"anatomy={self._anatomy}, "
            f"biometry={self._biometry}, "
            f"echo={self._echo}, "
            f"procedures={self._procedures}, "
            f"environment={self._environment}, "
            f"gestational={self._gestational})"
        )
