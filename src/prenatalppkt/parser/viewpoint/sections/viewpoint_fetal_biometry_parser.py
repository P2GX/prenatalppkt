import typing

from prenatalppkt.constants import (
    ABNORMAL_BPD_TERM,
    ABNORMAL_OFD_TERM,
    DECREASED_BPD_TERM,
    DECREASED_OFD_TERM,
    DEFAULT_BPD_HIGH,
    DEFAULT_BPD_LOW,
    DEFAULT_OFD_LOW,
    INCREASED_BPD_TERM,
    INCREASED_OFD_TERM,
)
from prenatalppkt.measurements.percentile_range import PercentileRange
from prenatalppkt.measurements.term_bin import TermBin


class ViewpointFetalBiometryParser:
    """
    Parse fetal biometry results from Viewpoint text export lines. The parser extracts BPD and OFD measurements, converts percentile strings into PercentileRange objects, and assigns HPO term bins based on percentile-defined thresholds.
    """

    def __init__(self, lines: typing.List[str]) -> None:
        lines = [line for line in lines if len(line.strip()) > 0]
        self._bpd = None
        self._ofd = None
        for line in lines:
            if line.strip().startswith("BPD"):
                self._bpd = self._parse_bpd_line(line.strip())
            elif line.strip().startswith("OFD"):
                self._ofd = self._parse_ofd_line(line.strip())

    def _check_field(self, line: str, parts: typing.List[str], expected: str, i: int):
        if parts[i] != expected:
            raise ValueError(
                f"Malformed BPD line {line} -- first field should be '{expected}' but was {parts[i]}"
            )

    def _get_ga(self, line: str, parts: typing.List[str], week: int, day: int) -> str:
        w = parts[week].strip()
        d = parts[day].strip()
        if not w.endswith("w"):
            raise ValueError(f"Malformed week for gestational age {w} in line {line}")
        if not d.endswith("d"):
            raise ValueError(f"Malformed day for gestational age {d} in line {line}")
        return f"G{w}{d}"

    def _get_percentile_str(self, line: str, field: str) -> str:
        p = field.strip()
        if not p.endswith("%"):
            raise ValueError(f"Malformed percentile {p} in line {line}")
        return p

    def get_percentile_range(self, perc: str) -> PercentileRange:
        """
        Convert a percentile string (e.g., '23%') into a PercentileRange. Supports special tokens such as '<1%' and '>99%'.

        Parameters
        ----------
        perc : str
            Percentile string ending with '%'.

        Returns
        -------
        PercentileRange
            The evaluated percentile bin.

        Raises
        ------
        ValueError
            If the percentile string is malformed.
        """
        if perc == "<1%":
            return PercentileRange.below_3p()
        elif perc == ">99%":
            return PercentileRange.above_97p()
        number_str = perc[:-1]  # remove trailing %
        try:
            p = float(number_str)
            return PercentileRange.evaluate(p)
        except ValueError:
            raise ValueError(
                f"Percentile is not a float: {number_str!r} in line: {perc!r}"
            )

    def _get_method(self, line: str, field: str) -> str:
        method = field.strip()
        acceptable_methods = {"Hadlock", "Nicolaides", "Chervenak"}
        if method not in acceptable_methods:
            raise ValueError(f"Did not recognize method {method} in line {line}")
        return method

    def _get_range_and_description(
        self, line: str, parts: typing.List[str]
    ) -> typing.Tuple[PercentileRange, str]:
        if len(parts) != 7:
            raise ValueError(f"Could not parse line {line} -- got parts {parts}")
        self._check_field(line, parts, "mm", 2)
        value = f"{parts[1]} {parts[2]}"
        ga = self._get_ga(line=line, parts=parts, week=3, day=4)
        perc = self._get_percentile_str(line=line, field=parts[5])
        method = self._get_method(line=line, field=parts[6])
        mes_res = self.get_percentile_range(perc=perc)
        description = f"{value} {perc}% at {ga} ({method})"
        return mes_res, description

    def _parse_bpd_line(self, line: str) -> TermBin:
        """
        The lines contain an arbitrary amount of whitespace characters
        We use split to get the components
        ['BPD', '87.1', 'mm', '35w', '1d', '89%', 'Hadlock']
        """
        parts = line.split()
        self._check_field(line, parts, "BPD", 0)
        mes_res, description = self._get_range_and_description(line=line, parts=parts)
        if mes_res <= DEFAULT_BPD_LOW:
            return TermBin.from_term(
                range=mes_res,
                term=DECREASED_BPD_TERM,
                normal=False,
                description=description,
            )
        elif mes_res >= DEFAULT_BPD_HIGH:
            return TermBin.from_term(
                range=mes_res,
                term=INCREASED_BPD_TERM,
                normal=False,
                description=description,
            )
        else:
            return TermBin.from_term(
                range=mes_res,
                term=ABNORMAL_BPD_TERM,
                normal=True,
                description=description,
            )

    def _parse_ofd_line(self, line: str) -> TermBin:
        """
        The lines contain an arbitrary amount of whitespace characters
        We use split to get the components
        ['OFD', '103.3', 'mm', '30w', '3d', '2%', 'Nicolaides']
        """
        parts = line.split()
        self._check_field(line, parts, "OFD", 0)
        perc_range, description = self._get_range_and_description(
            line=line, parts=parts
        )
        if perc_range <= DEFAULT_OFD_LOW:
            return TermBin.from_term(
                range=perc_range,
                term=DECREASED_OFD_TERM,
                normal=False,
                description=description,
            )
        elif perc_range >= DEFAULT_BPD_HIGH:
            return TermBin.from_term(
                range=perc_range,
                term=INCREASED_OFD_TERM,
                normal=False,
                description=description,
            )
        else:
            return TermBin.from_term(
                range=perc_range,
                term=ABNORMAL_OFD_TERM,
                normal=True,
                description=description,
            )

    @property
    def bpd(self) -> typing.Optional[TermBin]:
        """
        Return the parsed BPD TermBin, or None if not present in the input.
        """
        return self._bpd

    @property
    def ofd(self) -> typing.Optional[TermBin]:
        """
        Return the parsed OFD TermBin, or None if not present in the input.
        """
        return self._ofd
