"""Smoke tests for protea-runners bootstrap."""

from __future__ import annotations

from importlib.metadata import entry_points

import protea_runners
from protea_runners import baseline, knn, lightgbm


def test_version_is_string() -> None:
    assert isinstance(protea_runners.__version__, str)


def test_submodules_importable() -> None:
    assert hasattr(lightgbm, "plugin")
    assert hasattr(knn, "plugin")
    assert hasattr(baseline, "plugin")


def test_entry_points_registered() -> None:
    eps = entry_points(group="protea.runners")
    names = {ep.name for ep in eps}
    assert "lightgbm" in names
    assert "knn" in names
    assert "baseline" in names


def test_no_platform_imports_leak() -> None:
    import sys

    forbidden = {"sqlalchemy", "fastapi", "protea_core"}
    leaked = forbidden & set(sys.modules)
    assert not leaked, f"Forbidden modules leaked: {leaked}"
