"""
src/prenatalppkt/dto/fetus/observer/fetus_echo_data.py

Fetal echocardiography data grouping.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class FetusEchoData:
    """
    Grouped fetal echocardiography data from Observer JSON.

    Attributes:
        fetal_echo_anatomy: Detailed cardiac anatomy findings
        fetal_echo_measurements: Cardiac measurements (chamber dimensions, etc.)
        dm_echo: Doppler measurements and cardiac flow data
    """

    fetal_echo_anatomy: Optional[Any] = None
    fetal_echo_measurements: Optional[Any] = None
    dm_echo: Optional[Any] = None

    def __repr__(self) -> str:
        return (
            f"FetusEchoData("
            f"anatomy={'present' if self.fetal_echo_anatomy else 'absent'}, "
            f"measurements={'present' if self.fetal_echo_measurements else 'absent'}, "
            f"dm_echo={'present' if self.dm_echo else 'absent'})"
        )
