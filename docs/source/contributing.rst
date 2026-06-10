Contributing
============

The mechanics of adding a runner plugin are in
:doc:`runners` under "How to add a runner". This page covers the
conventions every runner honours and the development workflow.

Conventions
-----------

- **Plugin imports are cheap.** Heavy ML imports go inside the methods
  that need them, never at module top. Plugin discovery at
  ``protea-core`` startup must stay free of GPU and DataFrame
  dependencies.
- **Schema sha is mandatory** for any runner that produces a re-ranker
  booster. Store ``feature_schema_sha`` on the result so the platform can
  validate schema alignment at inference time.
- **Artifact-store URIs are the boundary** between training and
  inference. ``export`` returns a URI; ``protea-core`` downloads the
  artefact through ``ArtifactStore`` at registration time. No filesystem
  path crosses the boundary.
- **Reproducibility.** A runner's ``fit`` must record enough provenance
  (commit SHA, dataset id, hyperparameters resolved from defaults plus
  payload, seeds) on the ``RunResult`` for an ``ExperimentRun`` row to
  replay faithfully within 1 percent Fmax.
- **Fail loudly.** A method that is not yet implemented raises
  ``NotImplementedError`` with a precise pointer to the active code path
  and the migration task, never a silent no-op. The
  :class:`~protea_runners._base.StubRunner` base does this for you.

Development workflow
--------------------

All changes target ``develop``; ``main`` tracks stable releases only.

.. code-block:: bash

   git clone https://github.com/frapercan/protea-runners.git
   cd protea-runners
   git checkout develop
   git checkout -b feature/my-runner

   poetry install

   # verify locally before opening a pull request
   poetry run pytest
   poetry run ruff check .
   poetry run mypy --strict src tests
   poetry run python scripts/check_smells.py --target src

Open the pull request against ``develop``. Notable changes are tracked in
``CHANGELOG.md``.

CI gates
--------

The ``protea-runners`` repository CI runs ``ruff``, the smell-budget
check, ``mypy`` strict, and ``pytest`` with a coverage floor (the
contract-surface stubs sit at 100 percent). A separate ``docs`` workflow
builds the Sphinx site with warnings treated as errors, so keep the docs
build clean.

Building the docs
-----------------

The Sphinx docs build is opt-in:

.. code-block:: bash

   poetry install --with docs
   cd docs && make html
   # output: docs/build/html/index.html
