protea-runners
==============

``protea-runners`` is the experiment-runner layer of the PROTEA stack. It
holds the training and evaluation runners that PROTEA dispatches when a
user submits an experiment: the LightGBM re-ranker trainer, the KNN-only
baseline, and the reference baselines used as the floor in ablations.

The problem it solves
---------------------

PROTEA needs to grow new ways of training and scoring models (a new
re-ranker objective, a new baseline, a future neural head) without
editing the platform every time one is added. A runner is therefore a
*plugin*: a small class that implements one fixed interface and announces
itself through a Python ``entry_points`` group. ``protea-core`` discovers
runners by name at runtime and drives them through a uniform lifecycle.
It never imports this package directly, so adding or changing a runner is
a change here, not in the platform.

Three properties fall out of that design:

- **Isolation.** Heavy ML dependencies (LightGBM, CUDA libraries) are
  declared as optional extras in this package and never pulled into a
  ``protea-core`` install.
- **Reservation.** A runner name registered today cannot be claimed by
  another package. When an implementation migrates in, the dispatch path
  does not change at all.
- **Fail-loud stubs.** A runner that is registered but not yet
  implemented raises a precise error pointing at the active code path and
  the migration task, so a mis-routed dispatch fails fast instead of
  no-op'ing.

Status
------

The three runners shipped today are **contract-surface stubs**. They
subclass the contract, register through ``entry_points``, and pass the
discoverability and compliance suites, but their lifecycle methods raise
``NotImplementedError``. The active training and inference code still
lives elsewhere and migrates into the plugins on a schedule:

.. list-table::
   :header-rows: 1
   :widths: 16 30 18 36

   * - Runner
     - Role
     - Status
     - Active code path (until migration)
   * - :doc:`lightgbm <runners>`
     - LightGBM re-ranker training
     - Stub (real path in F2A.7)
     - ``protea-reranker-lab`` standalone repository
   * - :doc:`knn <runners>`
     - KNN-only baseline (no re-ranker)
     - Stub (real path in F2C)
     - ``protea-core.PredictGOTermsBatchOperation``
   * - :doc:`baseline <runners>`
     - Reference baselines (naive frequency, BLAST)
     - Stub (reserved)
     - none yet; reserved for the F-EXP narrative work

What lives here
---------------

::

    protea-runners/
        src/protea_runners/
            __init__.py          package version
            _base.py             StubRunner shared base (Extract Superclass)
            lightgbm/__init__.py LightgbmRunner + plugin instance
            knn/__init__.py      KnnRunner + plugin instance
            baseline/__init__.py BaselineRunner + plugin instance
        docs/source/             this documentation
        pyproject.toml           entry-point registrations + extras
        tests/                   compliance + discoverability suites

The whole package depends only on ``protea-contracts`` for the
:class:`~protea_contracts.ExperimentRunner` interface and the typed
``RunResult`` / ``EvalResult`` return shapes. It imports nothing from
``protea-core``, which is what keeps it installable on its own.

Where to go next
----------------

- :doc:`overview` explains the runner contract, the shared base, and how
  ``entry_points`` discovery works.
- :doc:`quickstart` installs the package and runs a real discovery and
  dispatch example.
- :doc:`runners` documents each runner (purpose, configuration, status)
  and how to add one of your own.
- :doc:`contributing` covers the development workflow and CI gates.
- :doc:`reference/index` is the generated API documentation.

.. toctree::
   :hidden:
   :maxdepth: 2

   overview
   quickstart
   runners
   contributing
   reference/index
