"""
src/prenatalppkt/dto/fetus_data.py

Top-level Data Transfer Object for a single fetus entry in the Observer JSON.
This class acts as a container for all sub-components parsed from the
'fetuses' array, including core metadata, quantitative measurements,
ratios, and estimated fetal weights (EFWs).
"""

import typing
from ..hpo.simple_term import SimpleTerm
from .fetuses.fetus_core_data import FetusCoreData
from .fetuses.measurements_data import MeasurementsData
from .fetuses.ratios_data import FetusRatiosData
from .fetuses.efw_data import FetusEfwData


class FetusData:
    """
    Data transfer object for fetal phenotype and attributes.

    Attributes:
        fetus: Core fetal metadata (see FetusCoreData)
        amioticfluid: Meaning undetermined
        amniocentesis: Meaning undetermined
        anatomy: Unknown (likely qualitative findings)
        bpp: Meaning undetermined
        dm_echo: Meaning undetermined
        efws: Estimated fetal weight data (see FetusEfwData)
        ectopic_preg: Meaning undetermined
        fbscvs: Meaning undetermined
        fetal_echo_anatomy: Meaning undetermined
        fetal_echo_measurements: Meaning undetermined
        fetalvessels: Meaning undetermined
        firsttrimester: Meaning undetermined
        impression: Meaning undetermined
        measurements: Quantitative biometric measurements (see MeasurementsData)
        nst: Meaning undetermined
        otherprocs: Meaning undetermined
        placenta: Meaning undetermined
        ratios: Computed biometric ratios (e.g., HC/AC) (see FetusRatiosData)
        uards: Meaning undetermined
        hpo_term_list: List of HPO phenotype terms extracted from anatomy text
    """

    _hpo_term_list: typing.List[SimpleTerm]

    def __init__(
        self,
        hpo_term_list: typing.List[SimpleTerm],
        fetus: typing.Optional[FetusCoreData] = None,
        measurements: typing.Optional[MeasurementsData] = None,
        ratios: typing.Optional[FetusRatiosData] = None,
        efws: typing.Optional[FetusEfwData] = None,
        amioticfluid: typing.Optional[typing.Any] = None,
        amniocentesis: typing.Optional[typing.Any] = None,
        anatomy: typing.Optional[typing.Any] = None,
        bpp: typing.Optional[typing.Any] = None,
        dm_echo: typing.Optional[typing.Any] = None,
        ectopic_preg: typing.Optional[typing.Any] = None,
        fbscvs: typing.Optional[typing.Any] = None,
        fetal_echo_anatomy: typing.Optional[typing.Any] = None,
        fetal_echo_measurements: typing.Optional[typing.Any] = None,
        fetalvessels: typing.Optional[typing.Any] = None,
        firsttrimester: typing.Optional[typing.Any] = None,
        impression: typing.Optional[typing.Any] = None,
        nst: typing.Optional[typing.Any] = None,
        otherprocs: typing.Optional[typing.Any] = None,
        placenta: typing.Optional[typing.Any] = None,
        uards: typing.Optional[typing.Any] = None,
    ) -> None:
        """Encapsulates phenotype and biometric data for one fetus."""
        self._hpo_term_list = hpo_term_list
        self._fetus = fetus
        self._measurements = measurements
        self._ratios = ratios
        self._efws = efws

        # Placeholder fields for additional Observer sub-sections
        self._amioticfluid = amioticfluid
        self._amniocentesis = amniocentesis
        self._anatomy = anatomy
        self._bpp = bpp
        self._dm_echo = dm_echo
        self._ectopic_preg = ectopic_preg
        self._fbscvs = fbscvs
        self._fetal_echo_anatomy = fetal_echo_anatomy
        self._fetal_echo_measurements = fetal_echo_measurements
        self._fetalvessels = fetalvessels
        self._firsttrimester = firsttrimester
        self._impression = impression
        self._nst = nst
        self._otherprocs = otherprocs
        self._placenta = placenta
        self._uards = uards

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def hpo_term_list(self) -> typing.List[SimpleTerm]:
        """Return list of HPO terms linked to fetal phenotype."""
        return self._hpo_term_list

    @property
    def fetus(self) -> typing.Optional[FetusCoreData]:
        """Core fetal attributes (fetus number, GA, gender, etc.)."""
        return self._fetus

    @property
    def measurements(self) -> typing.Optional[MeasurementsData]:
        """Quantitative biometric measurements."""
        return self._measurements

    @property
    def ratios(self) -> typing.Optional[FetusRatiosData]:
        """Computed biometric ratios (e.g., HC/AC)."""
        return self._ratios

    @property
    def efws(self) -> typing.Optional[FetusEfwData]:
        """Estimated fetal weight data."""
        return self._efws

    # -------------------------------------------------------------------------
    # Representation
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"FetusData("
            f"fetus={self._fetus}, "
            f"measurements={self._measurements}, "
            f"ratios={self._ratios}, "
            f"efws={self._efws})"
        )
