"""Shared base for the contract-surface stub runners.

Every plugin in this package is, today, a *contract-surface stub*: it
subclasses :class:`protea_contracts.ExperimentRunner`, registers through
the ``protea.runners`` entry-point group, and passes the discoverability
and ABC-compliance suites, but its lifecycle methods raise
:class:`NotImplementedError`. The real training and inference paths still
live in ``protea-core`` and ``protea-reranker-lab`` and migrate into the
plugins across master plan v3 (F2A.7 for LightGBM, F2C for KNN).

This module pulls the three identical lifecycle signatures and the
``NotImplementedError`` construction up into one place (the
*Extract Superclass* refactoring) so each concrete runner only declares
its :attr:`~StubRunner.name` and a per-method pointer to the active code
path. The phrase ``contract-surface stub`` is part of the contract that
the test-suite pins, so it is generated here once.
"""

from __future__ import annotations

from typing import Any, ClassVar, NoReturn

from protea_contracts import EvalResult, ExperimentRunner, RunResult


class StubRunner(ExperimentRunner):
    """Base class for runners whose lifecycle is not yet implemented.

    Subclasses set :attr:`name` and :attr:`stub_pointers` (a mapping of
    lifecycle method name to a human-readable pointer at the active code
    path / migration task). Each ``fit`` / ``evaluate`` / ``export`` call
    raises :class:`NotImplementedError` whose message always contains the
    phrase ``contract-surface stub`` followed by that pointer, so a
    mis-routed dispatcher fails fast with an actionable error instead of a
    silent no-op.
    """

    #: Canonical plugin name; matches the entry-point and the sub-package.
    name: str = ""

    #: Per-method pointer at the active code path, keyed by method name
    #: (``"fit"`` / ``"evaluate"`` / ``"export"``).
    stub_pointers: ClassVar[dict[str, str]] = {}

    def _stub(self, method: str) -> NoReturn:
        """Raise a uniform ``contract-surface stub`` error for *method*."""
        message = f"{type(self).__name__}.{method} is a contract-surface stub."
        pointer = self.stub_pointers.get(method)
        if pointer:
            message = f"{message} {pointer}"
        raise NotImplementedError(message)

    def fit(self, spec: dict[str, Any], dataset_uri: str, *, emit: Any) -> RunResult:
        """Train or prepare a model from a frozen dataset (stub)."""
        self._stub("fit")

    def evaluate(self, model_uri: str, eval_dataset_uri: str, *, emit: Any) -> EvalResult:
        """Compute held-out metrics for a trained model (stub)."""
        self._stub("evaluate")

    def export(self, run_id: str, output_uri: str, *, emit: Any) -> dict[str, Any]:
        """Persist a trained artefact to an ``ArtifactStore`` URI (stub)."""
        self._stub("export")
