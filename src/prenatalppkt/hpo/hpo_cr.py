"""
src/prenatalppkt/hpo/hpo_cr.py

Abstract base class for HPO concept recognizers
"""

import abc
from typing import List

from .simple_term import SimpleTerm


class HpoConceptRecognizer(metaclass=abc.ABCMeta):
    """
    This abstract class acts as an interface for classes that implement parse_cell to perform HPO-based concept recognition.
    """

    @abc.abstractmethod
    def parse(self, cell_contents, custom_d=None) -> List[SimpleTerm]:
        """
        parse HPO Terms from the contents of a cell of the original table

        :param cell_contents: a cell of the original table
        :type cell_contents: str
        :param custom_d: a dictionary with keys for strings in the original table and their mappings to HPO labels
        :type custom_d: Dict[str,str], optional
        """
        pass
