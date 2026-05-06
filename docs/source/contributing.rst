Adding a new runner
====================

Adding a runner plugin is a one-file commit in this repository plus
one line in ``pyproject.toml``. The platform learns about the new
runner through the ``protea.runners`` ``entry_points`` group.

Five steps
----------

1. **Create a sub-module** under
   ``src/protea_runners/<your_name>/__init__.py``. The directory name
   is the canonical plugin name and must match the ``name`` class
   attribute below.

2. **Implement the contract.** Subclass
   :class:`protea_contracts.ExperimentRunner` and provide ``fit``,
   ``evaluate`` and ``export``. Each returns a typed result
   object from ``protea-contracts``:

   .. code-block:: python

      from typing import Any
      from protea_contracts import EvalResult, ExperimentRunner, RunResult

      class MyRunner(ExperimentRunner):
          name = "myrunner"

          def fit(self, spec: dict[str, Any], *, emit: Any) -> RunResult:
              # Lazy import any heavy dependency here.
              import lightgbm
              ...
              return RunResult(...)

          def evaluate(self, spec: dict[str, Any], *, emit: Any) -> EvalResult:
              ...

          def export(self, spec: dict[str, Any], *, emit: Any) -> dict[str, Any]:
              ...

      plugin = MyRunner()

3. **Register the entry point.** In ``pyproject.toml`` add::

      [tool.poetry.plugins."protea.runners"]
      myrunner = "protea_runners.myrunner:plugin"

4. **Declare extras** for any heavy ML dependency you brought in::

      [tool.poetry.dependencies]
      lightgbm = { version = ">=4.0", optional = true }

      [tool.poetry.extras]
      myrunner = ["lightgbm"]

5. **Add tests** under ``tests/test_myrunner.py`` covering: instance
   type, ABC compliance, ``name`` attribute, discoverability via
   ``entry_points(group="protea.runners")``, and the public method
   signatures. Existing test files are templates.

Conventions
-----------

- **Plugin imports are cheap.** Heavy ML imports go inside the
  methods that need them, never at module top. Plugin discovery at
  ``protea-core`` startup must stay free of GPU / DataFrame
  dependencies.
- **Schema sha is mandatory** for any runner that produces a
  re-ranker booster. The runner must store
  ``feature_schema_sha`` on the result so the platform can validate
  schema alignment at inference time.
- **Artifact-store URIs** are the boundary between training and
  inference. ``export`` returns a URI; ``protea-core`` uses
  ``ArtifactStore`` to download the artefact at registration time.
  No filesystem paths cross the boundary.
- **Reproducibility**: a runner's ``fit`` must record enough
  provenance (commit SHA, dataset id, hyperparameters resolved from
  defaults + payload, seeds) on the ``RunResult`` for an
  ``ExperimentRun`` row to be replay-faithful within 1 % Fmax.

CI expectations
---------------

The ``protea-runners`` repository CI runs ``ruff``, ``mypy`` strict
and ``pytest`` with 100 % coverage on the contract-surface stubs.
Once F2A.7 lands the lightgbm trainer, the gate drops to 80 % to
reflect the larger surface that the trainer brings in.

Documentation
-------------

The Sphinx docs build is opt-in:

.. code-block:: bash

   poetry install --with docs
   cd docs && make html
