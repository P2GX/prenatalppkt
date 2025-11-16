"""
src/prenatalppkt/hpo/hpo_cr.py

Abstract base class for HPO concept recognizers
"""

import abc
from typing import List

# from .hp_term import HpTerm
from .simple_term import SimpleTerm  # Changed from HpTerm


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

    @abc.abstractmethod
    def parse_cell_for_exact_matches(self, cell_contents, custom_d) -> List[SimpleTerm]:
        """
        Identify HPO Terms from the contents of a cell whose label exactly matches a string in the custom dictionary

        :param cell_contents: a cell of the original table
        :type cell_contents: str
        :param custom_d: a dictionary with keys for strings in the original table and their mappings to HPO labels
        :type custom_d: Dict[str,str]
        """
        pass

    @abc.abstractmethod
    def get_term_from_id(self, hpo_id) -> SimpleTerm:
        """
        :param hpo_id: an HPO identifier, e.g., HP:0004372
        :type hpo_id: str
        :returns: corresponding HPO term
        :rtype: SimpleTerm
        """
        pass

    @abc.abstractmethod
    def get_term_from_label(self, label) -> SimpleTerm:
        """
        :param label: an HPO label, e.g., Arachnodactyly
        :type label: str
        :returns: corresponding HPO term
        :rtype: SimpleTerm
        """
        pass
