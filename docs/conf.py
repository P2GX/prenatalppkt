from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "prenatalppkt"
author = "Varenya Jain, Peter N. Robinson"
copyright = "2025-present, Varenya Jain and Peter N. Robinson"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "issues/*"]

html_theme = "pydata_sphinx_theme"
html_title = "prenatalppkt"
html_static_path: list[str] = []

html_theme_options = {
    "github_url": "https://github.com/P2GX/prenatalppkt",
    "navbar_align": "left",
    "show_toc_level": 2,
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "linkify",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autosummary_generate = True
napoleon_google_docstring = True
napoleon_numpy_docstring = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "phenopackets": ("https://phenopacket-schema.readthedocs.io/en/latest/", None),
}

nitpicky = False

if os.environ.get("READTHEDOCS") == "True":
    html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
