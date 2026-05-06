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
except Exception:  # noqa: BLE001
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

# When the lightgbm runner absorbs the lab in F2A.7, its heavy deps
# (lightgbm, pandas, scikit-learn) live behind extras and need
# mocking here. None are installed today; mock list ready.
autodoc_mock_imports = [
    "lightgbm",
    "pandas",
    "sklearn",
    "faiss",
    "torch",
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
