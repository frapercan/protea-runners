"""Reference baselines for reproducibility.

Implements :class:`protea_contracts.ExperimentRunner` as a thin shell
that runs CAFA-style reference baselines (e.g. naive frequency,
BLAST-based predictions) against a frozen dataset. The plugin is the
contract surface; no active baseline implementation lives in PROTEA
or the lab today, so the three lifecycle methods are stubs that
fail loud rather than no-op'ing.

Why this plugin exists pre-implementation: the master plan v3
narrative calls for ablation tables that compare PROTEA's reranker
against the same naive / BLAST baselines that CAFA evaluates. Having
the entry_point reserved means the experiment dispatch layer can
treat ``runner == "baseline"`` as a known unknown rather than an
unrecognised name.
"""

from __future__ import annotations

from typing import Any

from protea_contracts import EvalResult, ExperimentRunner, RunResult


class BaselineRunner(ExperimentRunner):
    """Reference baseline runner (naive frequency, BLAST, ...)."""

    name = "baseline"

    def fit(
        self,
        spec: dict[str, Any],
        dataset_uri: str,
        *,
        emit: Any,
    ) -> RunResult:
        """Fit reference baselines against the training dataset.

        Stub during F2A.8: no active baseline implementation exists
        yet. The plan is to land naive-frequency and BLAST-based
        baselines as part of the F-EXP narrative work.
        """
        raise NotImplementedError(
            "BaselineRunner.fit is a contract-surface stub. No active "
            "baseline implementation exists yet; this entry_point is "
            "reserved for the F-EXP narrative work in master plan v3."
        )

    def evaluate(
        self,
        model_uri: str,
        eval_dataset_uri: str,
        *,
        emit: Any,
    ) -> EvalResult:
        """Evaluate a baseline against a held-out dataset."""
        raise NotImplementedError(
            "BaselineRunner.evaluate is a contract-surface stub. No "
            "active baseline implementation exists yet; this is "
            "reserved for the F-EXP narrative work in master plan v3."
        )

    def export(
        self,
        run_id: str,
        output_uri: str,
        *,
        emit: Any,
    ) -> dict[str, Any]:
        """Export baseline predictions for ablation tables."""
        raise NotImplementedError(
            "BaselineRunner.export is a contract-surface stub. No active "
            "baseline implementation exists yet."
        )


#: Module-level plugin instance discovered via the
#: ``protea.runners`` entry_points group.
plugin = BaselineRunner()
