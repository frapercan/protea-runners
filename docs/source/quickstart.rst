Quickstart
==========

Install
-------

.. code-block:: bash

   pip install protea-runners

The package is dependency-light today (``protea-contracts``, ``numpy``,
``pyarrow``); the heavy ML stack for the LightGBM trainer lands behind a
``protea-runners[lightgbm]`` extra alongside F2A.7. Nothing pulls in a
GPU or ML framework at import time.

Discover the registered runners
-------------------------------

The platform resolves a runner by name through
``importlib.metadata.entry_points``. The same call works from any
environment where the package is installed:

.. code-block:: python

   from importlib.metadata import entry_points

   runners = entry_points(group="protea.runners")
   print(sorted(ep.name for ep in runners))
   # ['baseline', 'knn', 'lightgbm']

   plugin = runners["lightgbm"].load()
   print(plugin.name)
   # lightgbm

Call the lifecycle
------------------

Each plugin exposes the :doc:`runner contract <overview>` lifecycle.
Until the migrations land (F2A.7 for LightGBM, F2C for KNN) the methods
are stubs that fail loud with a pointer to the active code path:

.. code-block:: python

   from protea_runners.lightgbm import plugin as lightgbm_runner

   lightgbm_runner.fit({}, "s3://bucket/dataset/", emit=lambda *a, **k: None)
   # NotImplementedError: LightgbmRunner.fit is a contract-surface stub.
   # The active training pipeline lives in the protea-reranker-lab repo;
   # absorbing it into this plugin is F2A.7 of master plan v3 ...

The ``emit`` argument is the structured-event callback the platform
passes in; a no-op lambda is fine when calling a runner by hand.

Carry a spec
------------

A run references a runner by name inside a
:class:`protea_contracts.RerankerSpec`, which travels in the
``ExperimentRun.hparams`` JSONB column:

.. code-block:: python

   from protea_contracts import RerankerSpec

   spec = RerankerSpec.model_validate(
       {
           "runner": "lightgbm",
           "objective": "lambdarank",
           "enabled_feature_families": ["knn", "alignment_nw"],
           "seed": 17,
       }
   )
   assert spec.runner == "lightgbm"

The ``runner`` field is the dispatch key the worker uses to load the
plugin; the remaining fields configure the run once the trainer is live.

Next steps
----------

- :doc:`overview` for the full lifecycle interface and discovery model.
- :doc:`runners` for per-runner roles, configuration and status.
- :doc:`contributing` to add a runner of your own.
