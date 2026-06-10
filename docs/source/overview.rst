Overview and concepts
=====================

This page explains the three ideas that the rest of the package builds
on: the runner contract that every plugin implements, the shared base
the plugins use while their lifecycles are still stubs, and the
``entry_points`` mechanism that lets ``protea-core`` find them.

The runner contract
-------------------

Every plugin implements one interface,
:class:`protea_contracts.ExperimentRunner`. The platform resolves a
runner by name and drives it through three lifecycle methods:

.. list-table::
   :header-rows: 1
   :widths: 14 32 24 30

   * - Method
     - Inputs
     - Returns
     - Role
   * - ``fit``
     - ``spec: dict``, ``dataset_uri: str``, ``emit``
     - ``RunResult``
     - Train or prepare a model from a frozen dataset.
   * - ``evaluate``
     - ``model_uri: str``, ``eval_dataset_uri: str``, ``emit``
     - ``EvalResult``
     - Compute held-out CAFA metrics (Fmax, AuPRC, coverage per aspect).
   * - ``export``
     - ``run_id: str``, ``output_uri: str``, ``emit``
     - ``dict``
     - Persist the trained artefact to an ``ArtifactStore`` URI.

The return shapes are typed by ``protea-contracts``:
:class:`~protea_contracts.RunResult` carries a ``model_uri`` plus
``metrics`` and ``extras`` dicts; :class:`~protea_contracts.EvalResult`
carries ``metrics`` and ``extras``. Normalising the shapes is what lets
``protea-core`` record provenance uniformly across runners and lets the
reproducibility tooling replay any past run.

Four conventions hold across every runner:

- **``name`` is the dispatch key.** It must equal the entry-point name
  and the sub-package directory, and it must round-trip through the
  ``runner`` field of :class:`protea_contracts.RerankerSpec` so the
  worker can dispatch by ``spec.runner``.
- **``emit`` is a structured-event callback.** Runners report progress
  through it; they do not write to stdout for control flow.
- **URIs are the training and inference boundary.** ``export`` returns a
  store URI; the platform downloads the artefact through
  ``ArtifactStore`` at registration time. No filesystem path crosses the
  boundary.
- **Discovery stays cheap.** Heavy ML imports live inside the method that
  needs them, never at module top, so resolving a plugin at platform
  startup pulls in no GPU or DataFrame dependency.

The shared base
---------------

While the active training and inference paths still live in
``protea-core`` and ``protea-reranker-lab``, all three plugins share one
base class, :class:`protea_runners._base.StubRunner`. A recent
*Extract Superclass* refactoring lifted the three identical lifecycle
signatures and the ``NotImplementedError`` construction into this single
place, so each concrete runner only declares two things:

- ``name``: the canonical plugin name, matching the entry-point and the
  sub-package.
- ``stub_pointers``: a mapping from lifecycle method name (``"fit"`` /
  ``"evaluate"`` / ``"export"``) to a human-readable pointer at the
  active code path and the migration task.

Every stub error contains the phrase ``contract-surface stub`` followed
by that pointer. A mis-routed dispatch therefore fails immediately with
an actionable message instead of silently doing nothing. The phrase is
pinned by the test-suite, so it is generated once in the base rather than
repeated in each runner.

The full base-class API is in the :doc:`reference/index`.

Discovery through entry points
------------------------------

A runner advertises itself in ``pyproject.toml`` under the
``protea.runners`` entry-point group:

.. code-block:: toml

   [tool.poetry.plugins."protea.runners"]
   lightgbm = "protea_runners.lightgbm:plugin"
   knn = "protea_runners.knn:plugin"
   baseline = "protea_runners.baseline:plugin"

Each target points at a module-level ``plugin`` instance of the runner
class. ``protea-core`` resolves a runner by name through the standard
library, with no import dependency on this package:

.. code-block:: python

   from importlib.metadata import entry_points

   plugin = entry_points(group="protea.runners")["lightgbm"].load()
   plugin.fit({}, "s3://bucket/dataset/", emit=lambda *a, **k: None)
   # raises NotImplementedError until F2A.7

Because dispatch goes through the name and not an import, registering a
new runner (or swapping a stub for a real implementation) requires no
change in ``protea-core``.
