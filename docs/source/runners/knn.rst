KNN (``knn``)
=============

The KNN-only baseline runner: K-nearest-neighbour search over PLM
embeddings, GO transfer with cosine-similarity weighting, no
re-ranker layer. The runner exists primarily to make the KNN
baseline reproducible from a frozen dataset, useful for ablations
that contrast re-ranker vs raw KNN performance.

:Status: contract-surface stub.
:Real path until F2C: ``protea-core.predict_go_terms_batch``
                       (KNN + GO transfer). Lifted to
                       ``protea-method`` in F2C.1, then consumed
                       here without platform dependency.
:Lifecycle:
    - ``fit``: no-op in concept (KNN has no parameters to fit).
    - ``evaluate``: held-out CAFA-style metrics against an
      :class:`protea_contracts.EvalResult`.
    - ``export``: writes the configuration manifest plus the
      reference embedding cache; no booster artefact.

Operational notes
-----------------

- The platform's KNN cache is process-level and float16; restoring
  from an exported reference set must reproduce the same cache for
  bit-identical predictions.
- The ``knn`` runner does not need a per-runner extra; once F2C
  lands, it depends only on ``protea-method``.

API reference
-------------

.. automodule:: protea_runners.knn
   :members:
   :show-inheritance:
   :member-order: bysource
