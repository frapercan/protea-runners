"""LightGBM reranker training runner.

Implements :class:`protea_contracts.ExperimentRunner` as the
contract surface for the LightGBM training pipeline that today lives
in the ``protea-reranker-lab`` repository. The plugin is a shell
during F2A.8: real ``fit`` / ``evaluate`` / ``export`` come in
F2A.7 of master plan v3 (lab → ``protea-runners.lightgbm`` migration,
which is in the human-review queue and stays there until the user
green-lights the reranker-sensitive refactor).

Until F2A.7 lands, the active flow is unchanged:

  1. PROTEA's ``ExportResearchDatasetOperation`` publishes
     ``train.parquet`` + ``eval.parquet`` + ``manifest.json`` via the
     ``ArtifactStore``.
  2. The lab's ``pull_dataset.py`` resolves the dataset URI, trains a
     LightGBM booster, and writes ``runs/<run_id>/{model.txt,
     spec.yaml, run.json}``.
  3. PROTEA's ``POST /reranker-models/import-by-reference`` registers
     the trained booster.

Once F2A.7 lands, steps 2 and 3 become a single
``LightgbmRunner.fit`` invocation.
"""

from __future__ import annotations

from typing import Any

from protea_contracts import EvalResult, ExperimentRunner, RunResult


class LightgbmRunner(ExperimentRunner):
    """LightGBM reranker training runner."""

    name = "lightgbm"

    def fit(
        self,
        spec: dict[str, Any],
        dataset_uri: str,
        *,
        emit: Any,
    ) -> RunResult:
        """Train a LightGBM reranker booster from a frozen dataset.

        Stub during F2A.8: the active training implementation lives in
        ``protea-reranker-lab``. F2A.7 will absorb it into this plugin
        and replace the stub with the real training loop.
        """
        raise NotImplementedError(
            "LightgbmRunner.fit is a contract-surface stub. The active "
            "training pipeline lives in the protea-reranker-lab repo; "
            "absorbing it into this plugin is F2A.7 of master plan v3 "
            "(human-review-queued)."
        )

    def evaluate(
        self,
        model_uri: str,
        eval_dataset_uri: str,
        *,
        emit: Any,
    ) -> EvalResult:
        """Evaluate a trained LightGBM booster against a held-out dataset."""
        raise NotImplementedError(
            "LightgbmRunner.evaluate is a contract-surface stub. The "
            "active evaluation goes through PROTEA's "
            "RunCafaEvaluationOperation; merging into this runner is "
            "F2A.7 of master plan v3."
        )

    def export(
        self,
        run_id: str,
        output_uri: str,
        *,
        emit: Any,
    ) -> dict[str, Any]:
        """Export ``model.txt`` + ``spec.yaml`` + ``run.json`` triple."""
        raise NotImplementedError(
            "LightgbmRunner.export is a contract-surface stub. F2A.7 "
            "will move this from the lab's ``runs/<run_id>/`` writer."
        )


#: Module-level plugin instance discovered via the
#: ``protea.runners`` entry_points group.
plugin = LightgbmRunner()
