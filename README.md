# protea-runners

Experiment runner plugins for the [PROTEA](https://github.com/frapercan/protea)
stack. Each sub-module implements the `ExperimentRunner` ABC from
[`protea-contracts`](https://github.com/frapercan/protea-contracts)
and registers via the `protea.runners` `entry_points` group.

## Install

```bash
pip install protea-runners
```

Or, to install a specific runner with its optional heavy dependencies:

```bash
pip install "protea-runners[lightgbm]"   # LightGBM extras
pip install "protea-runners[all]"         # all runner extras
```

The runner contract is `fit` → `evaluate` → `export`: take a frozen
dataset URI, train a model, score it against a held-out split,
publish the produced artefact under a canonical layout. PROTEA's
`ExperimentRun` row tracks the lifecycle and resolves the runner by
name.

## Status — three contract-surface stubs today

| Sub-module | Runner | Status | Real implementation lives in |
|------------|--------|--------|------------------------------|
| `protea_runners.lightgbm` | LightGBM reranker training | **stub** | [`protea-reranker-lab`](https://github.com/frapercan/protea-reranker-lab); migrates here in F2A.7 |
| `protea_runners.knn` | KNN-only baseline (no reranker) | **stub** | PROTEA's `PredictGOTermsBatchOperation`; migrates here in F2C |
| `protea_runners.baseline` | Reference baselines (naive frequency, BLAST) | **stub** | not yet implemented; reserved for F-EXP narrative work |
| `protea_runners.gnn` | R-GCN over GO-DAG (PROTEA-DL) | future | post-defensa |
| `protea_runners.retrieval_neural` | Neural retrieval reranker | future | post-defensa |

Each stub plugin is an ABC-compliant subclass with `name` set, but
its `fit` / `evaluate` / `export` methods raise
`NotImplementedError` with a message naming the active code path
and the master-plan task that will move the implementation here.
Future grep on `LightgbmRunner.fit` lands the reader at the
migration-plan line in the docstring.

```python
from protea_runners.lightgbm import plugin as lightgbm

lightgbm.fit({}, "s3://bucket/dataset/", emit=lambda *a, **k: None)
# NotImplementedError: LightgbmRunner.fit is a contract-surface stub.
# The active training pipeline lives in the protea-reranker-lab repo;
# absorbing it into this plugin is F2A.7 of master plan v3.
```

## How experiment runs are dispatched

1. The user submits an `ExperimentRun` row via PROTEA's API
   referencing a runner by name (e.g. `lightgbm`).
2. `protea-core` resolves the runner via
   `entry_points(group="protea.runners")["lightgbm"].load()`.
3. The runner gets a `spec` dict, a frozen `dataset_uri`, and an
   `emit` callback. It trains, evaluates, and exports under the
   contract.
4. Results land back as a new `RerankerModel` (or equivalent) plus
   the `ExperimentRun` record metadata.

This dispatch is in place today via the F2B endpoints (see
[`GET /runners`](https://protea.readthedocs.io/) for the runtime
discovery surface). What's missing is the **inside** of `fit`,
`evaluate`, `export` for each runner — that lands as part of F2A.7
(LightGBM) and F2C (KNN).

## Why the stubs ship before the implementations

Two reasons:

1. **Entry-point reservation.** A name registered today cannot be
   accidentally reused by another package. When `lightgbm` actually
   migrates here, the entry-point already exists; the migration is
   purely a code change inside the plugin module.
2. **Failure mode is loud.** Calling `lightgbm.fit(...)` today
   raises a `NotImplementedError` with a precise pointer, not an
   `AttributeError` or a silent no-op. Mis-routed dispatchers fail
   immediately with actionable error messages.

## Adding a new runner

The full guide lives in the Sphinx docs under
`docs/source/contributing.rst`. Five-step summary:

1. Create `src/protea_runners/<your_name>/__init__.py`.
2. Subclass `ExperimentRunner` and implement `fit` + `evaluate` +
   `export`. Set `name = "<your_name>"`.
3. Register under `[tool.poetry.plugins."protea.runners"]` in
   `pyproject.toml`.
4. Declare any heavy deps as `optional = true` and add an extras
   group named after the plugin.
5. Mirror the existing test files (`tests/test_<your_name>.py`)
   covering instance type, ABC compliance, name attribute,
   discoverability, and the lifecycle stub semantics.

## Roadmap

| Phase | Task | Outcome |
|-------|------|---------|
| F2A.7 | LightGBM training migration | `protea-reranker-lab` absorbed into `protea_runners.lightgbm`. Real `fit`/`evaluate`/`export`. |
| F2C.1 | `protea-method` extraction (KNN) | KNN inference path moves to `protea-method`; `protea_runners.knn` becomes a thin wrapper. |
| F-EXP | Narrative baselines | `protea_runners.baseline` gets naive-frequency + BLAST implementations for ablation tables. |
| Post-defensa | GNN, retrieval-neural | New plugin modules for PROTEA-DL research extensions. |

## Development

```bash
poetry install
poetry run pytest             # 19 tests, ~0.1s
poetry run ruff check .
poetry run mypy --strict src
```

## Contributing

Contributions are welcome from research institutions and individual developers.

**Branch strategy:** all changes target `develop`; `main` tracks stable
releases only.

```bash
git clone https://github.com/frapercan/protea-runners.git
cd protea-runners
git checkout develop
git checkout -b feature/my-runner

poetry install

# Make your changes, then verify locally:
poetry run pytest             # 19 tests, < 1 s
poetry run ruff check .
poetry run mypy --strict src

# Open a pull request targeting develop
```

Key constraints:
- **Fail loudly.** If a runner method is not yet implemented, raise
  `NotImplementedError` with a precise pointer to the active code path
  and the migration task (e.g., `"active pipeline: protea-reranker-lab; migrates here in F2A.7"`).
- **Entry-point reservation.** New runners must register their entry
  point in `pyproject.toml` before the implementation is complete.
  Reserving the name early prevents accidental reuse.
- **No runtime deps on protea-core.** This package must stay installable
  without the full PROTEA platform.

## Documentation

Full Sphinx documentation in `docs/source/`. Each runner has its
own page documenting current status, the data shape it expects,
the artefacts it produces, and pointers to the active
implementation while the migration is pending.

## License

MIT. See `LICENSE`.

<!-- protea-stack:start -->

## Repositories in the PROTEA stack

Single source of truth: [`docs/source/_data/stack.yaml`](https://github.com/frapercan/PROTEA/blob/develop/docs/source/_data/stack.yaml) in PROTEA. Run `python scripts/sync_stack.py` to regenerate this block.

| Repo | Role | Status | Summary |
|------|------|--------|---------|
| [PROTEA](https://github.com/frapercan/PROTEA) | Platform | `active` | Backend platform. Hosts the ORM, job queue, FastAPI surface, frontend, and orchestration. |
| [protea-contracts](https://github.com/frapercan/protea-contracts) | Contracts | `beta` | Shared contract surface. ABCs, pydantic payloads, feature schema, schema_sha. Imported by every other repo. |
| [protea-method](https://github.com/frapercan/protea-method) | Inference | `skeleton` | Pure inference path (KNN, feature compute, reranker apply). Target of the F2C extraction. Bind-mounted by the LAFA containers. |
| [protea-sources](https://github.com/frapercan/protea-sources) | Source plugin | `skeleton` | Annotation source plugins (GOA, QuickGO, UniProt). Discovered via Python entry_points. |
| **protea-runners** (this repo) | Runner plugin | `skeleton` | Experiment runner plugins (LightGBM lab, KNN baseline, future GNN). Discovered via Python entry_points. |
| [protea-backends](https://github.com/frapercan/protea-backends) | Backend plugin | `skeleton` | Protein language model embedding backends (ESM family, T5/ProstT5, Ankh, ESM3-C). Discovered via Python entry_points. |
| [protea-reranker-lab](https://github.com/frapercan/protea-reranker-lab) | Lab | `active` | LightGBM reranker training lab. Pulls datasets from PROTEA, trains boosters, publishes them back via /reranker-models/import-by-reference. |
| [cafaeval-protea](https://github.com/frapercan/cafaeval-protea) | Evaluator | `active` | Standalone fork of cafaeval (CAFA-evaluator-PK) with the PK-coverage fix and a bit-exact parity guarantee against the upstream. |

<!-- protea-stack:end -->
