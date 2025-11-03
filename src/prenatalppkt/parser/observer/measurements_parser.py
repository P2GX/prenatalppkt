"""
src/prenatalppkt/parser/observer/measurements_parser.py
Parser for extracting biometric measurements from Observer JSON
"""

import typing
from prenatalppkt.dto.measurements_data import MeasurementsData, Measurement


class MeasurementsParser:
    """Simple parser for fetal biometric measurements."""

    def parse(self, json_data: typing.Dict) -> MeasurementsData:
        """
        Parse measurements from fetus JSON data.

        Args:
            json_data: Dictionary from fetuses[0] containing 'measurements' key

        Returns:
            MeasurementsData object with parsed measurements

        Raises:
            ValueError: If 'measurements' key not found
        """
        # Check for measurements key
        if "measurements" not in json_data:
            raise ValueError("Did not find 'measurements' key in input")

        measurements_list = json_data["measurements"]

        # Get fetus number from the nested 'fetus' dict
        fetus_number = 1  # default
        if "fetus" in json_data:
            fetus_number = json_data["fetus"].get("fetus_number", 1)

        # Parse each measurement
        measurements = []
        for m_dict in measurements_list:
            measurement = Measurement(
                label=m_dict.get("label", "Unknown"),
                value=float(m_dict.get("value", 0)),
                unit_of_measure=m_dict.get("unit_of_measure", "cm"),
                calculated_percentile=float(m_dict.get("calculated_percentile", 0)),
                calculated_z_score=float(m_dict.get("calculated_z_score", 0)),
                calculated_ega=float(m_dict.get("calculated_ega", 0)),
                fetus_number=int(m_dict.get("fetus_number", 1)),
            )
            measurements.append(measurement)

        return MeasurementsData(fetus_number=fetus_number, measurements=measurements)
