"""Smoke tests for the LightGBM runner plugin (F2A.8 of master plan v3).

The full migration of the protea-reranker-lab training pipeline into
this plugin is F2A.7 (human-review queue). These tests pin the
contract surface only.
"""

from __future__ import annotations

from importlib.metadata import entry_points

import pytest
from protea_contracts import ExperimentRunner

from protea_runners.lightgbm import LightgbmRunner, plugin


def test_plugin_is_lightgbm_runner_instance() -> None:
    assert isinstance(plugin, LightgbmRunner)


def test_plugin_implements_experiment_runner_abc() -> None:
    assert isinstance(plugin, ExperimentRunner)


def test_plugin_name_is_lightgbm() -> None:
    assert plugin.name == "lightgbm"


def test_plugin_resolvable_via_entry_points() -> None:
    eps = entry_points(group="protea.runners")
    lgbm_eps = [ep for ep in eps if ep.name == "lightgbm"]
    assert len(lgbm_eps) == 1
    resolved = lgbm_eps[0].load()
    assert resolved is plugin


def test_lifecycle_methods_raise_not_implemented_during_f2a8() -> None:
    noop_emit: object = lambda *a, **k: None  # noqa: E731
    with pytest.raises(NotImplementedError, match="contract-surface stub"):
        plugin.fit({}, "s3://demo/", emit=noop_emit)
    with pytest.raises(NotImplementedError, match="contract-surface stub"):
        plugin.evaluate("s3://m", "s3://d", emit=noop_emit)
    with pytest.raises(NotImplementedError, match="contract-surface stub"):
        plugin.export("run_42", "s3://out/", emit=noop_emit)
