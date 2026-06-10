"""LightGBM reranker training runner.

Implements :class:`protea_contracts.ExperimentRunner` (via
:class:`protea_runners._base.StubRunner`) as the contract surface for
the LightGBM training pipeline that today lives in the
``protea-reranker-lab`` repository. The plugin is a shell during F2A.8:
real ``fit`` / ``evaluate`` / ``export`` come in F2A.7 of master plan v3
(lab -> ``protea-runners.lightgbm`` migration, which is in the
human-review queue and stays there until the user green-lights the
reranker-sensitive refactor).

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

from typing import ClassVar

from protea_runners._base import StubRunner


class LightgbmRunner(StubRunner):
    """LightGBM reranker training runner.

    Stub during F2A.8: the active training implementation lives in
    ``protea-reranker-lab``. F2A.7 absorbs it into this plugin and
    replaces the stubs with the real training / evaluation / export loop.
    """

    name = "lightgbm"

    stub_pointers: ClassVar[dict[str, str]] = {
        "fit": (
            "The active training pipeline lives in the protea-reranker-lab "
            "repo; absorbing it into this plugin is F2A.7 of master plan v3 "
            "(human-review-queued)."
        ),
        "evaluate": (
            "The active evaluation goes through PROTEA's "
            "RunCafaEvaluationOperation; merging into this runner is F2A.7 "
            "of master plan v3."
        ),
        "export": (
            "F2A.7 will move this from the lab's ``runs/<run_id>/`` writer."
        ),
    }


#: Module-level plugin instance discovered via the
#: ``protea.runners`` entry_points group.
plugin = LightgbmRunner()
