"""Smoke tests for the Baseline runner plugin (F2A.8 of master plan v3)."""

from __future__ import annotations

from importlib.metadata import entry_points

import pytest
from protea_contracts import ExperimentRunner

from protea_runners.baseline import BaselineRunner, plugin


def test_plugin_is_baseline_runner_instance() -> None:
    assert isinstance(plugin, BaselineRunner)


def test_plugin_implements_experiment_runner_abc() -> None:
    assert isinstance(plugin, ExperimentRunner)


def test_plugin_name_is_baseline() -> None:
    assert plugin.name == "baseline"


def test_plugin_resolvable_via_entry_points() -> None:
    eps = entry_points(group="protea.runners")
    baseline_eps = [ep for ep in eps if ep.name == "baseline"]
    assert len(baseline_eps) == 1
    resolved = baseline_eps[0].load()
    assert resolved is plugin


def test_lifecycle_methods_raise_not_implemented_during_f2a8() -> None:
    noop_emit: object = lambda *a, **k: None  # noqa: E731
    with pytest.raises(NotImplementedError, match="contract-surface stub"):
        plugin.fit({}, "s3://demo/", emit=noop_emit)
    with pytest.raises(NotImplementedError, match="contract-surface stub"):
        plugin.evaluate("s3://m", "s3://d", emit=noop_emit)
    with pytest.raises(NotImplementedError, match="contract-surface stub"):
        plugin.export("run_42", "s3://out/", emit=noop_emit)
