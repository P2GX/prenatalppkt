"""
ontology.py

Ontology utilities for Prenatal Phenopackets (prenatalppkt).
Supports downloading and loading the Human Phenotype Ontology (HPO).
"""

from __future__ import annotations
import json
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

import logging

logger = logging.getLogger(__name__)

# HPO release URL (points to latest)
#HPO_URL = "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/hp.json"
# Utilize persistent uniform resource locator (PURL) over Github release URL
HPO_URL = "http://purl.obolibrary.org/obo/hp.json"

# Project-local cache (instead of ~/.cache)
CACHE_DIR = Path(__file__).resolve().parents[2] / "data"
HPO_CACHE = CACHE_DIR / "hp.json"


def ensure_cache_dir() -> None:
    """Ensure the ontology cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def download_hpo(force: bool = False) -> Path:
    """
    Download the HPO ontology JSON into project-local cache.

    Parameters
    ----------
    force : bool
        If True, overwrite existing file.

    Returns
    -------
    Path
        Path to the cached hp.json file.
    """
    ensure_cache_dir()
    if HPO_CACHE.exists() and not force:
        return HPO_CACHE

    logger.info("Downloading HPO ontology to: %s", HPO_CACHE)
    with urllib.request.urlopen(HPO_URL) as resp:
        data = resp.read()
    HPO_CACHE.write_bytes(data)
    return HPO_CACHE


class HPO:
    """Minimal wrapper for HPO JSON graph."""

    def __init__(self, hp_path: Optional[Path] = None):
        path = hp_path or HPO_CACHE
        if not path.exists():
            raise FileNotFoundError(
                f"HPO file not found at {path}. Run scripts/download_hpo.py first."
            )
        self._terms: Dict[str, Dict[str, Any]] = {}
        self._labels: Dict[str, str] = {}
        self._load(path)

    def _load(self, path: Path) -> None:
        obj = json.loads(path.read_text(encoding="utf-8"))
        graphs = obj.get("graphs", [])
        if not graphs:
            return
        for term in graphs[0].get("nodes", []):
            tid = term.get("id")
            lbl = term.get("lbl")
            if tid and lbl:
                self._terms[tid] = term
                self._labels[lbl.lower()] = tid

    def get_label(self, term_id: str) -> Optional[str]:
        """Return label for an HPO ID, or None if not found."""
        term = self._terms.get(term_id)
        return term.get("lbl") if term else None

    def get_id(self, label: str) -> Optional[str]:
        """Return ID for a given label (case-insensitive), or None if not found."""
        return self._labels.get(label.lower())

    def is_valid(self, term_id: str) -> bool:
        """Check if a given HPO ID exists."""
        return term_id in self._terms

    def search_label(self, text: str) -> list[str]:
        """Find term IDs whose labels contain the text (case-insensitive)."""
        t = text.lower()
        return [
            tid for tid, term in self._terms.items() if t in term.get("lbl", "").lower()
        ]
