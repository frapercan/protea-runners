"""Round-trip stability for the payloads protea-runners consumes.

Every runner plugin in this package takes a :class:`protea_contracts.RerankerSpec`
as the canonical ``fit`` spec input (per ``ExperimentRunner.fit``
signature). The spec travels in ``ExperimentRun.hparams`` JSONB; a
silent serialise / deserialise drift would crash the worker on
dequeue.

This module exercises the JSONB round-trip from this repo's vantage
point (the consumer side) so a breaking change in
:mod:`protea_contracts.payloads.RerankerSpec` is also caught by the
runners CI, not only by the contracts CI.
"""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any

import pytest
from protea_contracts import RerankerSpec

ENTRY_GROUP = "protea.runners"


def _discovered_plugins() -> list[Any]:
    eps = list(entry_points(group=ENTRY_GROUP))
    if not eps:
        pytest.fail(
            f"No entry points found under group {ENTRY_GROUP!r}; "
            "protea-runners is not installed or pyproject.toml is misconfigured."
        )
    return [ep.load() for ep in eps]


def test_reranker_spec_minimal_roundtrip() -> None:
    """``RerankerSpec`` with only ``runner`` set must round-trip."""
    spec = RerankerSpec.model_validate({"runner": "lightgbm"})
    rebuilt = RerankerSpec.model_validate(spec.model_dump())
    assert rebuilt == spec


def test_reranker_spec_full_roundtrip() -> None:
    """``RerankerSpec`` with every field set must round-trip in JSON mode.

    The JSON-mode path is the one the JSONB-backed Job.payload column
    travels; a silently-lossy dump here means worker crash on dequeue.
    """
    spec = RerankerSpec.model_validate(
        {
            "runner": "lightgbm",
            "objective": "lambdarank",
            "enabled_feature_families": ["knn", "alignment_nw"],
            "drop_features": ["distance"],
            "seed": 17,
            "extras": {"num_boost_round": 5000, "learning_rate": 0.05},
        }
    )
    rebuilt = RerankerSpec.model_validate(spec.model_dump(mode="json"))
    assert rebuilt == spec
    assert rebuilt.extras["num_boost_round"] == 5000


@pytest.mark.parametrize("runner_name", ["lightgbm", "knn", "baseline"])
def test_reranker_spec_accepts_every_registered_runner_name(runner_name: str) -> None:
    """The spec's ``runner`` field must accept every plugin's name.

    Catches drift where a runner is renamed in pyproject.toml /
    plugin source but the contracts-side ``runner`` field validator
    rejects the new value (pin-test against future "runner" -> Literal
    typing without coordinating with the plugin pack).
    """
    spec = RerankerSpec.model_validate({"runner": runner_name})
    assert spec.runner == runner_name


def test_every_plugin_name_is_a_valid_reranker_spec_runner() -> None:
    """Symmetric guard: every loaded plugin's ``.name`` must round-trip via the spec.

    The PROTEA worker dispatches by ``RerankerSpec.runner`` -> entry_point
    name; a plugin whose name fails ``RerankerSpec`` validation would
    be silently unreachable. This test crosses the contract boundary
    in the opposite direction from ``test_contract_compliance``.
    """
    failures: list[str] = []
    for plugin in _discovered_plugins():
        try:
            spec = RerankerSpec.model_validate({"runner": plugin.name})
        except Exception as exc:
            failures.append(f"{plugin.name!r}: {exc}")
            continue
        if spec.runner != plugin.name:
            failures.append(
                f"{plugin.name!r} round-trip mismatched: spec.runner={spec.runner!r}"
            )
    assert not failures, (
        "Some plugin names cannot be carried by RerankerSpec: "
        + "; ".join(failures)
    )
