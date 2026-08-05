"""
src/prenatalppkt/hpo/fast_hpo_cr_cr.py

Concept recognizer backed by the fast_hpo_cr (FastHPOCR) text -> HPO engine.

Requires the optional ``fast_hpo_cr`` extra (``uv sync --extra fast_hpo_cr``) -
never installed by default, never the default recognizer. FastHPOCR is a
two-step engine: an index must be built from ``hp.obo`` once before any text
can be annotated, unlike fenominal/ferrific which build their index from
``hp.json`` at construction time. FastHPOCR's own README claims ~3 minutes
for this - measured directly against a real, current hp.obo, it took ~19
minutes, so plan for that real figure rather than the documented one. This
module fetches ``hp.obo`` and builds/caches the index on first use, reusing
the cached files on every later construction.
"""

import os
import typing
from pathlib import Path

import requests

from .hpo_cr import HpoConceptRecognizer
from .simple_term import SimpleTerm

HP_OBO_URL = "https://purl.obolibrary.org/obo/hp.obo"

# Namespaced subdirectory under the shared ontology cache root
# (~/.hpo-toolkit) - clearly a fast_hpo_cr-specific artifact, not confused
# with other tools' managed files there.
DEFAULT_CACHE_DIR = Path.home() / ".hpo-toolkit" / "fast_hpo_cr_index"


class FastHpoCrConceptRecognizer(HpoConceptRecognizer):
    """
    Recognize HPO concepts in free text using fast_hpo_cr (FastHPOCR).

    fast_hpo_cr has no negation detection (confirmed by reading its full source -
    no negation logic exists anywhere in the package), so every returned
    SimpleTerm has ``excluded=False`` - a real limitation, not an oversight.
    Uses ``longestMatch=True`` to match the non-overlapping output shape every
    other recognizer in this module produces; fast_hpo_cr's own real default
    (``longestMatch=False``) returns every overlapping candidate instead.
    """

    def __init__(self, cache_dir: typing.Optional[Path] = None) -> None:
        # Imported here, not at module level, so importing this module never
        # requires FastHPOCR/pronto to be installed unless this class is
        # actually instantiated - keeps the optional dependency truly optional.
        from FastHPOCR.HPOAnnotator import HPOAnnotator
        from FastHPOCR.IndexHPO import IndexHPO
        from FastHPOCR.util.CRConstants import HP_INDEX_FILE

        cache_dir = cache_dir or DEFAULT_CACHE_DIR
        cache_dir.mkdir(parents=True, exist_ok=True)
        index_path = cache_dir / HP_INDEX_FILE

        if not index_path.is_file():
            hp_obo_path = cache_dir / "hp.obo"
            if not hp_obo_path.is_file():
                _download(HP_OBO_URL, hp_obo_path)
            IndexHPO(str(hp_obo_path), str(cache_dir)).index()
            # IndexHPO.index() fails silently (prints an error and returns)
            # rather than raising if its prerequisites check fails - confirm
            # the index actually landed, or fail here with a clear message
            # instead of a confusing "file not found" from HPOAnnotator below.
            if not index_path.is_file():
                raise RuntimeError(
                    f"FastHPOCR IndexHPO did not produce {index_path} - "
                    f"check that {hp_obo_path} is a valid hp.obo file"
                )

        self._annotator = HPOAnnotator(str(index_path))

    def parse(self, cell_contents, custom_d=None) -> typing.List[SimpleTerm]:
        """Recognize HPO terms in free text via fast_hpo_cr.

        ``custom_d`` is accepted for interface compatibility but ignored;
        fast_hpo_cr performs recognition itself. ``excluded`` is always
        False - fast_hpo_cr has no negation detection.
        """
        text = str(cell_contents).replace("\n", " ")
        hits = self._annotator.annotate(text, longestMatch=True)
        return [
            SimpleTerm(hpo_id=hit.hpoUri, hpo_label=hit.hpoLabel, excluded=False)
            for hit in hits
        ]


def _download(url: str, dest: Path) -> None:
    temp = dest.with_suffix(dest.suffix + ".tmp")
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with open(temp, "wb") as f:
            for chunk in response.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    os.replace(temp, dest)
