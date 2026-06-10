The runner contract
===================

Every plugin in this package implements one interface:
:class:`protea_contracts.ExperimentRunner`. The platform never imports a
runner directly; it resolves one by name through the
``protea.runners`` entry-point group and drives it through three
lifecycle methods. This page is the reference for that interface and for
the shared stub base the plugins use today.

Lifecycle
---------

.. list-table::
   :header-rows: 1
   :widths: 14 30 26 30

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

Conventions every runner honours:

- **``name`` is the dispatch key.** It must equal the entry-point name
  and the sub-package directory, and it must round-trip through
  :class:`protea_contracts.RerankerSpec` so the worker can dispatch by
  ``spec.runner``.
- **``emit`` is a structured-event callback.** Runners report progress
  through it; they never write to stdout for control flow.
- **URIs are the training/inference boundary.** ``export`` returns a
  store URI; the platform downloads the artefact through
  ``ArtifactStore`` at registration time. No filesystem path crosses the
  boundary.
- **Discovery stays cheap.** Heavy ML imports live inside the method that
  needs them, never at module top, so plugin discovery at platform
  startup pulls in no GPU or DataFrame dependency.

Stub base
---------

While the active training and inference paths still live in
``protea-core`` and ``protea-reranker-lab``, the three plugins share a
single :class:`~protea_runners._base.StubRunner` base. It pulls the
identical lifecycle signatures and the ``NotImplementedError``
construction up into one place (the *Extract Superclass* refactoring), so
each concrete runner only declares its ``name`` and a per-method pointer
to the active code path. Every stub error contains the phrase
``contract-surface stub`` followed by that pointer, so a mis-routed
dispatch fails fast with an actionable message instead of a silent no-op.

.. automodule:: protea_runners._base
   :members:
   :show-inheritance:
   :member-order: bysource
