"""KNN-only baseline runner (no reranker).

Implements :class:`protea_contracts.ExperimentRunner` for the
no-reranker baseline: ``predict_go_terms`` style KNN over
embeddings, GO transfer with cosine-similarity weighting, no
LightGBM rescore. The plugin is the contract surface; the active
inference path lives in PROTEA's ``PredictGOTermsBatchOperation``
and stays there until F2C of master plan v3 hoists the inference
core into a package both PROTEA and protea-runners can depend on.

Note on ``fit`` / ``evaluate`` / ``export``: KNN has no parameters
to fit, so ``fit`` is a no-op in concept. The runner's reason to
exist is reproducible *evaluation* of the KNN baseline against a
frozen dataset, useful for ablations comparing reranker vs KNN-only.
All three methods are contract-surface stubs during F2A.8.
"""

from __future__ import annotations

from typing import Any

from protea_contracts import EvalResult, ExperimentRunner, RunResult


class KnnRunner(ExperimentRunner):
    """KNN-only baseline runner (no reranker layer)."""

    name = "knn"

    def fit(
        self,
        spec: dict[str, Any],
        dataset_uri: str,
        *,
        emit: Any,
    ) -> RunResult:
        """KNN has no parameters to fit; this is a no-op shell.

        F2C will replace this with a fit that captures the K, distance
        metric, and embedding-config provenance into a portable artefact
        so a baseline run can be re-executed deterministically.
        """
        raise NotImplementedError(
            "KnnRunner.fit is a contract-surface stub. KNN is fit-free; "
            "the active KNN inference lives in PROTEA's "
            "PredictGOTermsBatchOperation. Migration is scheduled for "
            "F2C of master plan v3."
        )

    def evaluate(
        self,
        model_uri: str,
        eval_dataset_uri: str,
        *,
        emit: Any,
    ) -> EvalResult:
        """Evaluate KNN against a held-out dataset.

        Stub during F2A.8: real implementation will run KNN over
        ``eval_dataset_uri`` and produce CAFA Fmax / AuPRC / coverage
        per aspect.
        """
        raise NotImplementedError(
            "KnnRunner.evaluate is a contract-surface stub. The active "
            "evaluation path goes through PROTEA's "
            "RunCafaEvaluationOperation. Migration is scheduled for "
            "F2C of master plan v3."
        )

    def export(
        self,
        run_id: str,
        output_uri: str,
        *,
        emit: Any,
    ) -> dict[str, Any]:
        """Export KNN provenance + per-protein top-K predictions.

        Stub during F2A.8.
        """
        raise NotImplementedError(
            "KnnRunner.export is a contract-surface stub. Migration is "
            "scheduled for F2C of master plan v3."
        )


#: Module-level plugin instance discovered via the
#: ``protea.runners`` entry_points group.
plugin = KnnRunner()
