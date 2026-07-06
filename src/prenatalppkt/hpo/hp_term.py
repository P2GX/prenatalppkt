"""
src/prenatalppkt/hpo/hp_term.py
"""

import hpotk
import pandas as pd
import typing
from phenopackets.schema.v2 import TimeElement
from prenatalppkt.hpo.simple_term import SimpleTerm


class HpTerm:
    """
    Class to represent a phenotypic observation as an HPO term with optional modifiers

    :param hpo_id: a Human Phenotype Ontology (HPO) identifier such as HP:0001166
    :type hpo_id: str
    :param label: The HPO label that corresponds to the id (note: This class does not check for correct match)
    :type label: str
    :param observed: a boolean that indicates whether the HPO term was observed (True) or excluded (False)
    :type observed: bool
    :param measured: a boolean that indicates whether the HPO was measured (True) or not explicitly measured (False)
    :type measured: bool
    :param onset: an ISO8601 string representing the age of onset, optional
    :type onset: str
    :param resolution: an ISO8601 string representing the age of resolution, optional
    :type resolution: str
    """

    def __init__(
        self,
        hpo_id: str,
        label: str,
        observed: bool = True,
        measured: bool = True,
        onset: typing.Optional[TimeElement] = None,
        resolution: typing.Optional[TimeElement] = None,
    ):
        if hpo_id is None or len(hpo_id) == 0 or not hpo_id.startswith("HP"):
            raise ValueError(f"invalid id argument: '{hpo_id}'")
        if label is None or len(label) == 0:
            raise ValueError(f"invalid label argument: '{label}'")
        self._id = hpo_id
        self._label = label
        self._observed = observed
        self._measured = measured
        self._onset = onset
        self._resolution = resolution

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self._id == other._id
                and self._label == other._label
                and self._measured == other._measured
                and self._onset == other._onset
                and self._resolution == other._resolution
            )
        else:
            return NotImplemented

    def __hash__(self):
        return hash(
            (
                self._id,
                self._label,
                self._observed,
                self._measured,
                self._onset,
                self._resolution,
            )
        )

    @property
    def id(self) -> str:
        """
        :returns: The HPO identifier, e.g., HP:0001166
        :rtype: str
        """
        return self._id

    @property
    def label(self) -> str:
        """
        :returns: The HPO label, e.g., Arachnodactyly
        :rtype: str
        """
        return self._label

    @property
    def observed(self) -> bool:
        """
        :returns: True if this feature was observed (i.e., present)
        :rtype: bool
        """
        return self._observed

    @property
    def measured(self) -> bool:
        """
        :returns: True iff a measurement to assess this abnormality (HpTerm) was performed
        :rtype: bool
        """
        return self._measured

    @property
    def onset(self) -> typing.Optional[TimeElement]:
        """
        :returns: A TimeElement representing the age this abnormality first was observed
        :rtype: typing.Optional[TimeElement]
        """
        return self._onset

    def set_onset(self, onset: TimeElement) -> None:
        """
        Assign onset information to the HPO term
        """
        if not isinstance(onset, TimeElement):
            raise ValueError(
                f"argument of set_onset must be TimeElement but was {type(onset)}"
            )
        self._onset = onset

    @property
    def resolution(self) -> typing.Optional[TimeElement]:
        """
        :returns: A TimeElement representing the age this abnormality resolved
        :rtype: typing.Optional[TimeElement]
        """
        return self._resolution

    @property
    def display_value(self) -> str:
        """
        :returns: One of three strings describing the status of the term: "not measured", "excluded", or "observed"
        :rtype: str
        """
        if not self._measured:
            return "not measured"
        if not self._observed:
            return "excluded"
        else:
            return "observed"

    @property
    def hpo_term_and_id(self) -> str:
        """
        :returns: A string such as Arachnodactyly (HP:0001166) for display
        :rtype: str
        """
        return f"{self._label} ({self._id})"

    def _term_and_id_with_onset(self) -> str:
        if self._onset is not None:
            return f"{self.hpo_term_and_id}: onset {self._onset}"
        else:
            return self.hpo_term_and_id

    def __str__(self) -> str:
        if not self._measured:
            return f"not measured: {self._label} ({self._id})"
        elif not self._observed:
            return f"excluded: {self._term_and_id_with_onset()}"
        else:
            return self._term_and_id_with_onset()

    def to_string(self) -> str:
        """
        Return string representation of HPO term
        """
        return self.__str__()

    def excluded(self) -> None:
        """
        Sets the current term to excluded (i.e., the abnormality was sought but explicitly ruled out clinically)
        """
        self._observed = False

    @staticmethod
    def term_list_to_dataframe(hpo_list) -> pd.DataFrame:
        """
        Convert list of HpTerm objects into a pandas DataFrame
        """
        if not isinstance(hpo_list, list):
            raise ValueError(
                f"hpo_list argument must be a list but was {type(hpo_list)}"
            )
        if len(hpo_list) > 0:
            hpo1 = hpo_list[0]
            if not isinstance(hpo1, HpTerm):
                raise ValueError(
                    f"hpo_list argument must consist of HpTerm objects but had {type(hpo1)}"
                )
        if len(hpo_list) == 0:
            return pd.DataFrame(columns=["Col1", "Col2", "Col3"])
        items = []
        for hp in hpo_list:
            d = {
                "id": hp.id,
                "label": hp.label,
                "observed": hp.observed,
                "measured": hp.measured,
            }
            items.append(d)
        return pd.DataFrame(items)

    @staticmethod
    def from_hpo_tk_term(hpotk_term: hpotk.Term) -> "HpTerm":
        """Create a pyphetools HpTerm object from an hpo-toolkit Term object

        :param hpotk_term: A term from the HPO toolkit
        :type hpotk_term: hpotk.Term
        :returns: The corresponding HpTerm object
        :rtype: HpTerm
        """
        hpo_id = hpotk_term.identifier.value
        hpo_label = hpotk_term.name
        return HpTerm(hpo_id=hpo_id, label=hpo_label)

    # Add this method to HpTerm class:
    def to_simple_term(self) -> SimpleTerm:
        """
        Convert this HpTerm to a lightweight SimpleTerm.

        Returns:
            SimpleTerm with just ID, label, and exclusion status
        """
        return SimpleTerm(
            hpo_id=self._id,
            hpo_label=self._label,
            excluded=not self._observed,
            gestational_age=None,
        )


class HpTermBuilder:
    """
    Builder for constructing HpTerm objects with chained methods
    """

    def __init__(self, hpo_id: str, hpo_label: str):
        if not hpo_id.startswith("HP:"):
            raise ValueError(f"Malformed HPO id {hpo_id}")
        if len(hpo_id) != 10:
            raise ValueError(f"Malformed HPO id with length {len(hpo_id)}: {hpo_id}")
        self._hpo_id = hpo_id
        if hpo_label is None or len(hpo_label) < 3:
            raise ValueError(f'Malformed HPO label "{hpo_label}"')
        self._hpo_label = hpo_label
        self._observed = True
        self._measured = True
        self._onset = None
        self._resolution = None

    def excluded(self):
        """
        Mark the term as excluded (i.e., not observed)
        """
        self._observed = False
        return self

    def not_measured(self):
        """
        Mark the term as not measured
        """
        self._measured = False
        return self
