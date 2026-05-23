"""Sphinx configuration for ``protea-runners``."""

from __future__ import annotations

import os
import sys
from importlib.metadata import version as _pkg_version

sys.path.insert(0, os.path.abspath("../../src"))

project = "protea-runners"
author = "Francisco Miguel Pérez Canales"
copyright = "2026, Francisco Miguel Pérez Canales"

try:
    release = _pkg_version("protea-runners")
except Exception:
    release = "0.0.1"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
]

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "special-members": "__init__",
    "exclude-members": "__weakref__,__init_subclass__,__subclasshook__",
}
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# protea_contracts is a git-dep not installed in the docs venv.
# The heavy ML extras (lightgbm, pandas, scikit-learn) also live
# behind extras and are mocked here.  When F2A.7 lands and the deps
# are declared as proper package extras, this list shrinks.
autodoc_mock_imports = [
    "protea_contracts",
    "lightgbm",
    "pandas",
    "sklearn",
    "faiss",
    "torch",
    "numpy",
    "pyarrow",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

html_theme = "shibuya"
html_title = "protea-runners"
html_static_path: list[str] = []

templates_path = ["_templates"]
exclude_patterns: list[str] = []

master_doc = "index"
