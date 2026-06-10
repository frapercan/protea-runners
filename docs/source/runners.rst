Runners guide
=============

One section per runner, then a recipe for adding your own. Each runner is
a :doc:`contract-surface stub <overview>` today: the page documents the
intended role and configuration, the active code path that will be
absorbed, and the migration phase that turns the stub into a real
implementation. The generated API for each class is in the
:doc:`reference/index`.

LightGBM (``lightgbm``)
-----------------------

**Purpose.** The LightGBM re-ranker trainer. It trains a gradient-boosted
model on per-candidate features (embedding distance, alignment
statistics, taxonomic distance, ontology-ancestry vectors, per-PLM PCA
projections) to re-score the candidates produced by the KNN stage. This
is the runner behind PROTEA's production re-ranker.

**Configuration.** A run is described by a
:class:`protea_contracts.RerankerSpec`: ``objective`` (the LightGBM
objective, defaulting to ``lambdarank``), ``enabled_feature_families``
and ``drop_features`` to control the feature set, ``seed`` for
determinism, and an ``extras`` dict for trainer-specific options. Once
implemented, ``fit`` returns a :class:`~protea_contracts.RunResult` whose
``model_uri`` points at the stored booster and whose ``metrics`` /
``extras`` carry the training metrics (AUC, logloss, F1 at threshold
0.5), the feature ``schema_sha``, and the gain-based feature importance.

**Status.** Stub during F2A.8. The active training pipeline lives in the
`protea-reranker-lab <https://github.com/frapercan/protea-reranker-lab>`_
repository, which consumes a dataset published by PROTEA's
``ExportResearchDatasetOperation``, trains a booster, and re-imports it
through ``POST /reranker-models/import-by-reference``. F2A.7 absorbs that
trainer into this plugin as the canonical home for training; the
artifact-store boundary stays the same, only the trainer's repository
home changes.

Two facts to keep in mind once the trainer lands here:

- **Schema sha is load-bearing.** Inference refuses to apply a booster
  whose stored ``feature_schema_sha`` does not match the live registry.
  See :func:`protea_contracts.compute_schema_sha` and the canonical
  feature schema in ``protea-contracts``.
- **Heavy deps move behind an extra.** ``lightgbm``, ``pandas`` and
  ``scikit-learn`` land in a ``protea-runners[lightgbm]`` extra, so
  plugin discovery stays cheap whether or not the extra is installed.

KNN (``knn``)
-------------

**Purpose.** The KNN-only baseline: k-nearest-neighbour search over PLM
embeddings, GO transfer with cosine-similarity weighting, and no
re-ranker layer. Its reason to exist is reproducible evaluation of the
KNN baseline from a frozen dataset, which is what ablations contrasting
re-ranker against raw KNN performance need.

**Configuration.** A run captures the neighbourhood size ``K``, the
distance metric, and the embedding-config provenance, so the same
baseline can be re-executed deterministically. ``fit`` is conceptually a
no-op because KNN has no parameters to fit; ``evaluate`` produces
held-out CAFA-style metrics; ``export`` writes the configuration manifest
plus the reference embedding cache rather than a booster artefact.

**Status.** Stub during F2A.8. The active inference path is PROTEA's
``PredictGOTermsBatchOperation``, with evaluation going through
``RunCafaEvaluationOperation``. F2C of master plan v3 lifts the KNN
inference core out of ``protea-core`` into ``protea-method``; this runner
then consumes it without a platform dependency, and needs no per-runner
extra. The platform's KNN cache is process-level and float16, so
restoring from an exported reference set must reproduce the same cache for
bit-identical predictions.

Baseline (``baseline``)
-----------------------

**Purpose.** The reference baselines that serve as the floor in ablation
studies: naive frequency (sampling GO terms from the empirical frequency
distribution of the references, ignoring the embeddings) and a candidate
BLAST-based transfer variant. Anything that does not beat these baselines
is suspect.

**Configuration.** Deliberately un-tuned. The naive variant's predictions
reflect only the prior on GO terms in the reference set; the planned
BLAST variant compares alignment-based transfer against the same
evaluation harness. The selected variant is the only real knob.

**Status.** Stub, reserved. No active baseline implementation exists yet
in ``protea-core`` or the lab, so all three lifecycle methods fail loud
rather than no-op'ing. Reserving the ``baseline`` entry point lets the
dispatch layer treat ``runner == "baseline"`` as a known unknown rather
than an unrecognised name. The implementation lands as part of the F-EXP
narrative work, either as a runner here or as a fixed seed inside the
evaluation pipeline.

How to add a runner
-------------------

Adding a runner is a one-file change in this package plus one line in
``pyproject.toml``. The platform learns about it through the
``protea.runners`` entry-point group.

1. **Create a sub-module** at
   ``src/protea_runners/<your_name>/__init__.py``. The directory name is
   the canonical plugin name and must equal the ``name`` attribute.

2. **Implement the contract.** Subclass
   :class:`protea_contracts.ExperimentRunner` and provide ``fit``,
   ``evaluate`` and ``export``, each returning a typed result object:

   .. code-block:: python

      from typing import Any
      from protea_contracts import EvalResult, ExperimentRunner, RunResult

      class MyRunner(ExperimentRunner):
          name = "myrunner"

          def fit(self, spec: dict[str, Any], dataset_uri: str, *, emit: Any) -> RunResult:
              import lightgbm  # lazy-import any heavy dependency here
              ...
              return RunResult(model_uri="s3://...")

          def evaluate(self, model_uri: str, eval_dataset_uri: str, *, emit: Any) -> EvalResult:
              ...

          def export(self, run_id: str, output_uri: str, *, emit: Any) -> dict[str, Any]:
              ...

      plugin = MyRunner()

   If the lifecycle is not ready yet, subclass
   :class:`protea_runners._base.StubRunner` instead and declare
   ``stub_pointers`` so the stub error names the active code path.

3. **Register the entry point** in ``pyproject.toml``:

   .. code-block:: toml

      [tool.poetry.plugins."protea.runners"]
      myrunner = "protea_runners.myrunner:plugin"

4. **Declare extras** for any heavy dependency the runner imports:

   .. code-block:: toml

      [tool.poetry.dependencies]
      lightgbm = { version = ">=4.0", optional = true }

      [tool.poetry.extras]
      myrunner = ["lightgbm"]

5. **Add tests** at ``tests/test_myrunner.py`` covering instance type,
   ABC compliance, the ``name`` attribute, discoverability via
   ``entry_points(group="protea.runners")``, and the lifecycle semantics.
   The existing test files are templates.

The :doc:`contributing` page covers the conventions a runner must honour
and the CI gates each change passes.
