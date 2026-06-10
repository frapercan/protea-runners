# protea-runners

[![CI](https://github.com/frapercan/protea-runners/actions/workflows/ci.yml/badge.svg)](https://github.com/frapercan/protea-runners/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/readthedocs/protea-runners.svg)](https://protea-runners.readthedocs.io)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](https://unlicense.org/)
[![PyPI](https://img.shields.io/pypi/v/protea-runners.svg)](https://pypi.org/project/protea-runners/)

Experiment runner plugins for the
[PROTEA](https://github.com/frapercan/PROTEA) stack.
Each sub-module implements the `ExperimentRunner` ABC from
[`protea-contracts`](https://github.com/frapercan/protea-contracts)
and registers via the `protea.runners` `entry_points` group so that
`protea-core` can discover and dispatch runners by name at runtime
without a hard import dependency on this package.

**Status:** v0.0.1, production. Entry points `lightgbm`, `knn`, and `baseline`
are registered and discoverable. The implementations are contract-surface stubs;
the active LightGBM training pipeline lives in
[`protea-reranker-lab`](https://github.com/frapercan/protea-reranker-lab) and
migrates here in F2A.7.

<!-- protea-stack:start -->

## Repositories in the PROTEA stack

Single source of truth:
[`docs/source/_data/stack.yaml`](https://github.com/frapercan/PROTEA/blob/develop/docs/source/_data/stack.yaml)
in PROTEA. Run `python scripts/sync_stack.py` to regenerate this block.

| Repo | Role | Status | Summary |
|------|------|--------|---------|
| [PROTEA](https://github.com/frapercan/PROTEA) | Platform | `active` | Backend platform. Hosts the ORM, job queue, FastAPI surface, frontend, and orchestration. |
| [protea-contracts](https://github.com/frapercan/protea-contracts) | Contracts | `active` | Shared contract surface. ABCs, pydantic payloads, feature schema, schema_sha. Imported by every other repo. |
| [protea-method](https://github.com/frapercan/protea-method) | Inference | `active` | LAFA submission layer. Pure inference path (KNN, feature compute, reranker apply). Published to DockerHub; bind-mounted by LAFA containers. |
| [protea-sources](https://github.com/frapercan/protea-sources) | Source plugin | `active` | Annotation source plugins (GOA, QuickGO, UniProt, InterPro). Discovered via Python entry_points. |
| **protea-runners** (this repo) | Runner plugin | `active` | Experiment runner plugins (LightGBM, KNN, baseline). Entry points registered; real training lives in protea-reranker-lab (migrates here in F2A.7). |
| [protea-backends](https://github.com/frapercan/protea-backends) | Backend plugin | `active` | Protein language model embedding backends (ESM family, T5/ProstT5, Ankh, ESM3-C). Discovered via Python entry_points. |
| [protea-reranker-lab](https://github.com/frapercan/protea-reranker-lab) | Lab | `active` | LightGBM reranker training lab. Pulls datasets from PROTEA, trains boosters, publishes them back via /reranker-models/import-by-reference. |
| [cafaeval-protea](https://github.com/frapercan/cafaeval-protea) | Evaluator | `active` | Standalone fork of cafaeval (CAFA-evaluator-PK) with the PK-coverage fix and a bit-exact parity guarantee against the upstream. |

<!-- protea-stack:end -->

---

## What and why

A PROTEA experiment run references a runner by name (`lightgbm`, `knn`,
`baseline`). The platform resolves that name to a Python object via
`importlib.metadata.entry_points(group="protea.runners")["<name>"].load()`
and calls the standard `fit` / `evaluate` / `export` lifecycle.
This package owns those entry-point registrations and the ABC-compliant
classes behind them.

Keeping runners in a dedicated package has three advantages:

1. **Isolation.** Heavy ML deps (LightGBM, CUDA libraries) are
   declared as optional extras here and never pulled in by
   `protea-core` at install time.
2. **Entry-point reservation.** A name registered today cannot be
   accidentally claimed by another package. When the implementation
   migrates here, the dispatch layer does not change at all.
3. **Fail loudly.** Each stub raises `NotImplementedError` with a
   precise pointer to the active code path and the migration task.
   Mis-routed dispatchers fail immediately with an actionable message,
   not a silent no-op.

---

## Runners at a glance

| Plugin | Role | Status | Active code path until migration |
|--------|------|--------|----------------------------------|
| `lightgbm` | LightGBM reranker training | stub | [`protea-reranker-lab`](https://github.com/frapercan/protea-reranker-lab); migrates in F2A.7 |
| `knn` | KNN-only baseline (no reranker) | stub | `protea-core.PredictGOTermsBatchOperation`; migrates in F2C |
| `baseline` | Reference baselines (naive frequency, BLAST) | stub | reserved for F-EXP narrative work |
| `gnn` | R-GCN over GO-DAG (PROTEA-DL) | future | post-defensa |
| `retrieval_neural` | Neural retrieval reranker | future | post-defensa |

---

## Install

```bash
pip install protea-runners
```

With optional heavy extras for the LightGBM runner (available once F2A.7 lands):

```bash
pip install "protea-runners[lightgbm]"
pip install "protea-runners[all]"
```

The package is dependency-light today: only `protea-contracts`,
`numpy`, and `pyarrow`. No GPU or ML framework is pulled in at
import time.

---

## Quick example

Verify that entry-points are discoverable:

```python
from importlib.metadata import entry_points

runners = entry_points(group="protea.runners")
print([r.name for r in runners])
# ['lightgbm', 'knn', 'baseline']

plugin = runners["lightgbm"].load()
print(plugin.name)
# lightgbm
```

Call a lifecycle method (currently stubs):

```python
from protea_runners.lightgbm import plugin as lightgbm_runner

lightgbm_runner.fit({}, "s3://bucket/dataset/", emit=lambda *a, **k: None)
# NotImplementedError: LightgbmRunner.fit is a contract-surface stub.
# The active training pipeline lives in the protea-reranker-lab repo;
# absorbing it into this plugin is F2A.7 of the master plan.
```

The runner contract: `fit` takes a spec dict and a frozen dataset URI,
trains or prepares a model, and returns a `RunResult`. `evaluate` takes
a model URI and an eval dataset URI and returns an `EvalResult` with
per-aspect CAFA Fmax, AuPRC, and coverage. `export` serialises the
artefact to an `ArtifactStore` URI and returns a provenance dict.

---

## How experiment runs are dispatched

1. A user submits an `ExperimentRun` row via `POST /experiments/runs`,
   referencing a runner by name (e.g. `lightgbm`).
2. `protea-core` resolves the runner via
   `entry_points(group="protea.runners")["lightgbm"].load()`.
3. The runner receives a `spec` dict, a frozen `dataset_uri`, and an
   `emit` callback. It trains, evaluates, and exports under the
   contract.
4. Results land as a new `RerankerModel` row (or equivalent) plus the
   `ExperimentRun` lifecycle metadata.

The dispatch is in place via the F2B endpoints. What is missing is the
inside of `fit`, `evaluate`, `export` for each runner: that lands in
F2A.7 (LightGBM) and F2C (KNN).

---

## Architecture

```
protea-runners/
    src/
        protea_runners/
            __init__.py          # package version
            _base.py             # StubRunner shared base (Extract Superclass)
            lightgbm/
                __init__.py      # LightgbmRunner + plugin instance
            knn/
                __init__.py      # KnnRunner + plugin instance
            baseline/
                __init__.py      # BaselineRunner + plugin instance
    docs/source/
        conf.py                  # Sphinx config (shibuya theme)
        index.rst                # narrative intro + what-lives-here map
        overview.rst             # contract, shared base, entry-point discovery
        quickstart.rst           # install + discover + dispatch
        runners.rst              # per-runner guide + how to add a runner
        contributing.rst         # conventions, workflow, CI gates
        reference/index.rst      # generated API reference (autodoc)
    pyproject.toml               # entry_point registrations + extras
    tests/                       # ABC compliance + discoverability tests
```

The contract boundary: `protea_contracts.ExperimentRunner` is the ABC;
`RunResult` and `EvalResult` are the typed return shapes. This package
must stay installable without the full PROTEA platform. It imports
nothing from `protea-core`.

---

## Adding a new runner

The full guide is in the Sphinx docs under `docs/source/runners.rst`
("How to add a runner"). Five-step summary:

1. Create `src/protea_runners/<your_name>/__init__.py`.
2. Subclass `ExperimentRunner` and implement `fit` + `evaluate` +
   `export`. Set `name = "<your_name>"`.
3. Register under `[tool.poetry.plugins."protea.runners"]` in
   `pyproject.toml`.
4. Declare any heavy deps as `optional = true` and add an extras
   group named after the plugin.
5. Mirror the existing test files (`tests/test_<your_name>.py`)
   covering instance type, ABC compliance, name attribute,
   discoverability, and lifecycle stub semantics.

Key constraints:

- **Fail loudly.** If a runner method is not yet implemented, raise
  `NotImplementedError` with a precise pointer to the active code path
  and the migration task.
- **Entry-point reservation.** Register the entry point in
  `pyproject.toml` before the implementation is complete.
- **No runtime deps on protea-core.** This package must stay
  installable without the full PROTEA platform.
- **Schema sha is mandatory** for runners that produce a reranker
  booster. Store `feature_schema_sha` on the `RunResult` so the
  platform can validate schema alignment at inference time.

---

## Roadmap

| Phase | Task | Outcome |
|-------|------|---------|
| F2A.7 | LightGBM training migration | `protea-reranker-lab` absorbed into `protea_runners.lightgbm`. Real `fit`/`evaluate`/`export`. |
| F2C.1 | `protea-method` extraction (KNN) | KNN inference path moves to `protea-method`; `protea_runners.knn` becomes a thin wrapper. |
| F-EXP | Narrative baselines | `protea_runners.baseline` gets naive-frequency and BLAST implementations for ablation tables. |
| Post-defensa | GNN, retrieval-neural | New plugin modules for PROTEA-DL research extensions. |

---

## Development

```bash
poetry install
poetry run pytest             # contract + discoverability suites, < 1 s
poetry run ruff check .
poetry run mypy --strict src tests
poetry run python scripts/check_smells.py --target src
```

Published documentation: [https://protea-runners.readthedocs.io](https://protea-runners.readthedocs.io).

Build the Sphinx docs locally:

```bash
poetry install --with docs
cd docs && make html
# Output: docs/build/html/index.html
```

---

## Contributing

All changes target `develop`; `main` tracks stable releases only.

```bash
git clone https://github.com/frapercan/protea-runners.git
cd protea-runners
git checkout develop
git checkout -b feature/my-runner

poetry install

# Make changes, then verify locally:
poetry run pytest
poetry run ruff check .
poetry run mypy --strict src

# Open a pull request targeting develop
```

Contributions are welcome from research institutions and individual
developers. Notable changes are tracked in
[`CHANGELOG.md`](CHANGELOG.md).

---

## License

Released into the public domain under [The Unlicense](https://unlicense.org/).
See [`LICENSE`](LICENSE). You can copy, modify, publish, use, compile, sell, or
distribute this software, for any purpose, commercial or non-commercial, and by
any means.
