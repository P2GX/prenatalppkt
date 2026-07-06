import hpotk
import logging
import os
import typing
from hpotk.store import OntologyType
from prenatalppkt.hpo.fenominal_cr import FenominalConceptRecognizer

logger = logging.getLogger(__name__)


class HpoParser:
    """
    Class to retrieve and parse the HPO JSON file using the HPO-Toolkit

    Users probably will want to set the `release` option (e.g. `v2024-03-06` for the last release
    as of the time of this writing) or pass the path to the `hp.json` file via `hpo_json_file` option.

    Both options are optional, and the last HPO release will be used by default. The `release` has a priority
    over `hpo_json_file`.

    :param hpo_json_file: a `str` with a URL pointing to a remote `hp.json` (only ``http`` and ``https`` protocols
    are supported (no ``file``, ``ftp``)) or a path to a local `hp.json` file.
    :param release: an optional `str` with the HPO release tag or `None` if the latest HPO release should be used.
    """

    def __init__(
        self,
        hpo_json_file: typing.Optional[str] = None,
        release: typing.Optional[str] = None,
    ):
        if release is not None:
            store = hpotk.configure_ontology_store()
            self._ontology = store.load_hpo(release=release)
            self._hpo_json_file = store.resolve_store_path(
                OntologyType.HPO, release=release
            )
        elif hpo_json_file is not None:
            if not hpo_json_file.startswith("http") and not os.path.isfile(
                hpo_json_file
            ):
                raise FileNotFoundError(
                    f"Could not find hp.json file at {hpo_json_file}"
                )
            self._ontology = hpotk.load_ontology(hpo_json_file)
            self._hpo_json_file = hpo_json_file
        else:
            store = hpotk.configure_ontology_store()
            self._ontology = store.load_hpo()
            self._hpo_json_file = store.resolve_store_path(OntologyType.HPO)

        # Build the recognizer now, while hp.json is present; fenominal loads the
        # file into memory here, so the file may be removed afterwards.
        self._concept_recognizer = FenominalConceptRecognizer(self._hpo_json_file)

    def get_ontology(self) -> hpotk.Ontology:
        """
        :returns: a reference to the HPO
        """
        return self._ontology

    def get_id_to_label_map(self) -> typing.Mapping[str, str]:
        """
        :returns: a map from HPO term ids to HPO labels
        :rtype: Dict[str,str]
        """
        id_to_label_d = {}

        for term in self._ontology.terms:
            id_to_label_d[term.identifier.value] = term.name

        return id_to_label_d

    def get_hpo_concept_recognizer(self) -> FenominalConceptRecognizer:
        """
        Return initialized HPO concept recognizer
        """
        return self._concept_recognizer

    def get_version(self) -> typing.Optional[str]:
        """
        Return ontology version string, if available
        """
        return self._ontology.version
