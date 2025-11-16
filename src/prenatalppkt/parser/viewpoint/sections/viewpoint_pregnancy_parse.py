#
#

import typing
import re



N_FETUSES_REGEX = r"Number of fetuses: (\d)"


class ViewpointPregnancyParser:
    def __init__(self, lines: typing.List[str]):
        text = ";".join([line for line in lines if len(line.strip()) > 0])
        if "Singleton" in text:
            self._n_pregnancies = 1
        match = re.search(N_FETUSES_REGEX, text)
        if match:
            self._n_pregnancies = int(match.group(1))
        else:
            raise ValueError(f"Did not understand pregnancy line {text}")

    def n_pregnancies(self) -> int:
        return self._n_pregnancies
