"""KNN-only baseline runner (no reranker).

Implements :class:`protea_contracts.ExperimentRunner` (via
:class:`protea_runners._base.StubRunner`) for the no-reranker baseline:
``predict_go_terms`` style KNN over embeddings, GO transfer with
cosine-similarity weighting, no LightGBM rescore. The plugin is the
contract surface; the active inference path lives in PROTEA's
``PredictGOTermsBatchOperation`` and stays there until F2C of master
plan v3 hoists the inference core into a package both PROTEA and
protea-runners can depend on.

Note on ``fit`` / ``evaluate`` / ``export``: KNN has no parameters to
fit, so ``fit`` is a no-op in concept. The runner's reason to exist is
reproducible *evaluation* of the KNN baseline against a frozen dataset,
useful for ablations comparing reranker vs KNN-only. All three methods
are contract-surface stubs during F2A.8.
"""

from __future__ import annotations

from typing import ClassVar

from protea_runners._base import StubRunner


class KnnRunner(StubRunner):
    """KNN-only baseline runner (no reranker layer).

    Stub during F2A.8. F2C lifts the KNN inference core out of PROTEA so
    this runner can re-execute a baseline deterministically (capturing K,
    distance metric, and embedding-config provenance) without a platform
    dependency.
    """

    name = "knn"

    stub_pointers: ClassVar[dict[str, str]] = {
        "fit": (
            "KNN is fit-free; the active KNN inference lives in PROTEA's "
            "PredictGOTermsBatchOperation. Migration is scheduled for F2C "
            "of master plan v3."
        ),
        "evaluate": (
            "The active evaluation path goes through PROTEA's "
            "RunCafaEvaluationOperation. Migration is scheduled for F2C of "
            "master plan v3."
        ),
        "export": "Migration is scheduled for F2C of master plan v3.",
    }


#: Module-level plugin instance discovered via the
#: ``protea.runners`` entry_points group.
plugin = KnnRunner()
