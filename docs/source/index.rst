protea-runners
==============

Experiment runner plugins for the PROTEA stack. Each sub-module
implements the :class:`protea_contracts.ExperimentRunner` ABC and
registers via the ``protea.runners`` ``entry_points`` group.

A runner abstracts the lifecycle of a model: ``fit`` (train or
prepare), ``evaluate`` (compute metrics on a held-out split),
``export`` (persist the trained artefact). The contract normalises
the return shapes so ``protea-core`` can record provenance uniformly
across runners and reproducibility tools can replay any past run.

Status
------

The three plugins shipped today are **contract-surface stubs**: they
subclass the ABC, register through ``entry_points``, and pass the
discoverability tests, but their lifecycle methods raise
``NotImplementedError``. The active inference and training paths
still live in ``protea-core/operations/predict_go_terms.py``
(KNN, baseline) and the standalone
`protea-reranker-lab <https://github.com/frapercan/protea-reranker-lab>`_
repository (LightGBM training).

The migration plan in master plan v3:

- **F2A.7**: ``lightgbm`` runner absorbs ``protea-reranker-lab`` and
  becomes the canonical home for booster training. After F2A.7,
  ``protea-runners[lightgbm]`` provides the trainer.
- **F2C.1**: ``protea-method`` extraction lifts the inference core
  out of ``protea-core``; the ``knn`` runner then consumes it
  cleanly without depending on the platform.

At a glance
-----------

.. list-table::
   :header-rows: 1
   :widths: 16 26 22 36

   * - Plugin
     - Role
     - Status
     - Active code path (until migration)
   * - :doc:`knn <runners/knn>`
     - KNN-only baseline (no re-ranker)
     - Stub (real path in F2C)
     - ``protea-core.predict_go_terms_batch``
   * - :doc:`baseline <runners/baseline>`
     - Random / null baseline for ablations
     - Stub
     - n/a (future)
   * - :doc:`lightgbm <runners/lightgbm>`
     - LightGBM re-ranker
     - Stub (real path in F2A.7)
     - ``protea-reranker-lab`` standalone repo

Install
-------

.. code-block:: bash

   pip install protea-runners

The package is dependency-light today (only ``protea-contracts``);
extras for the heavy ML stack land alongside F2A.7.

Discovery
---------

``protea-core`` resolves a runner by name through
``importlib.metadata.entry_points``::

    from importlib.metadata import entry_points
    plugin = entry_points(group="protea.runners")["lightgbm"].load()
    plugin.fit(spec=...)  # raises NotImplementedError until F2A.7

Contents
--------

.. toctree::
   :maxdepth: 2

   runners/index
   contributing
