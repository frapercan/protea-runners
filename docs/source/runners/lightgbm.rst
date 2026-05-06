LightGBM (``lightgbm``)
========================

The LightGBM re-ranker runner. Trains a binary classifier on
per-candidate features (embedding distance, alignment statistics,
taxonomic distance, ontology ancestry vectors, per-PLM PCA
projections) and produces a booster that re-scores candidates from
the KNN stage.

:Status: contract-surface stub.
:Real path until F2A.7:
    `protea-reranker-lab <https://github.com/frapercan/protea-reranker-lab>`_
    standalone repository. The lab currently consumes a
    ``Dataset`` row published by PROTEA's
    ``ExportResearchDatasetOperation``, trains a booster, and
    re-imports it through ``POST /reranker-models/import-by-reference``.
:F2A.7 plan: absorb the lab into ``protea_runners.lightgbm`` as the
              canonical home for training. The same artifact-store
              boundary remains; only the trainer's repo home changes.

Lifecycle
---------

- ``fit(spec)``: trains a LightGBM booster from a frozen
  ``Dataset`` (resolved by id or name). Returns a ``RunResult``
  carrying the booster bytes, the schema sha (to be stored on
  the ``RerankerModel`` row at registration), training metrics
  (AUC, logloss, F1 at threshold 0.5), and the gain-based feature
  importance.
- ``evaluate(spec)``: runs CAFA-style evaluation
  (``cafaeval``) and returns an ``EvalResult`` with per-aspect
  Fmax, AUPR and coverage.
- ``export(spec)``: serialises the trained booster + manifest,
  uploads through the configured ``ArtifactStore`` (local FS or
  MinIO) and returns the storage URI for registration.

Operational notes
-----------------

- **Schema sha is load-bearing**. Inference refuses to apply a
  booster whose stored ``feature_schema_sha`` does not match the
  live registry. See :class:`protea_contracts.compute_schema_sha`
  and the canonical schema in ``protea-contracts.feature_schema``.
- **Heavy deps behind extras**. Once F2A.7 lands, ``lightgbm``,
  ``pandas`` and ``scikit-learn`` move into a
  ``protea-runners[lightgbm]`` extra. Plugin discovery stays
  cheap regardless.
- **Selective re-ranking**. The current production policy applies
  the re-ranker only to category / aspect cells where it improves
  over the KNN baseline; the rest fall back to KNN automatically.
  See the v18-selective configuration history for details.

API reference
-------------

.. automodule:: protea_runners.lightgbm
   :members:
   :show-inheritance:
   :member-order: bysource
