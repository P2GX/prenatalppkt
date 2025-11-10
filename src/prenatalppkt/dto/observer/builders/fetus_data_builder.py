"""
src/prenatalppkt/dto/observer/builders/fetus_data_builder.py

Builder for constructing FetusData objects with semantic groupings.
This reduces the constructor from 21 parameters to 7 logical groups.
"""

from typing import TYPE_CHECKING, Optional
from ..fetuses.fetus_core_data import FetusCoreData
from .fetus_anatomy_data import FetusAnatomyData
from .fetus_biometry_data import FetusBiometryData
from .fetus_echo_data import FetusEchoData
from .fetus_procedures_data import FetusProceduresData
from .fetus_environment_data import FetusEnvironmentData
from .fetus_gestational_data import FetusGestationalData

if TYPE_CHECKING:
    from prenatalppkt.dto.fetus_data import FetusData


class FetusDataBuilder:
    """
    Fluent builder for constructing FetusData with semantic field groupings.

    Example:
        fetus_data = (
            FetusDataBuilder(fetus_core)
            .with_anatomy(anatomy_data)
            .with_biometry(biometry_data)
            .with_echo(echo_data)
            .build()
        )
    """

    def __init__(self, fetus_core: FetusCoreData):
        """
        Initialize builder with required core fetal metadata.

        Args:
            fetus_core: Core fetal attributes (fetus number, GA, gender, etc.)
        """
        if not isinstance(fetus_core, FetusCoreData):
            raise TypeError(f"fetus_core must be FetusCoreData, got {type(fetus_core)}")

        self._fetus_core = fetus_core
        self._anatomy: Optional[FetusAnatomyData] = None
        self._biometry: Optional[FetusBiometryData] = None
        self._echo: Optional[FetusEchoData] = None
        self._procedures: Optional[FetusProceduresData] = None
        self._environment: Optional[FetusEnvironmentData] = None
        self._gestational: Optional[FetusGestationalData] = None

    def with_anatomy(self, anatomy: FetusAnatomyData) -> "FetusDataBuilder":
        """Attach anatomy findings and impressions."""
        self._anatomy = anatomy
        return self

    def with_biometry(self, biometry: FetusBiometryData) -> "FetusDataBuilder":
        """Attach biometric measurements, ratios, and EFWs."""
        self._biometry = biometry
        return self

    def with_echo(self, echo: FetusEchoData) -> "FetusDataBuilder":
        """Attach fetal echocardiography data."""
        self._echo = echo
        return self

    def with_procedures(self, procedures: FetusProceduresData) -> "FetusDataBuilder":
        """Attach prenatal procedures and assessments."""
        self._procedures = procedures
        return self

    def with_environment(self, environment: FetusEnvironmentData) -> "FetusDataBuilder":
        """Attach fetal environment data (fluids, vessels, placenta)."""
        self._environment = environment
        return self

    def with_gestational(self, gestational: FetusGestationalData) -> "FetusDataBuilder":
        """Attach early pregnancy and gestational data."""
        self._gestational = gestational
        return self

    def build(self) -> "FetusData":
        """
        Construct and return the final FetusData object.

        Returns:
            FetusData: Complete fetal data with all attached components
        """
        # Import here to avoid circular dependency
        from prenatalppkt.dto.fetus_data import FetusData

        return FetusData(
            fetus_core=self._fetus_core,
            anatomy=self._anatomy,
            biometry=self._biometry,
            echo=self._echo,
            procedures=self._procedures,
            environment=self._environment,
            gestational=self._gestational,
        )
