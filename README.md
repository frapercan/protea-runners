# protea-runners

Experiment runner plugins for the [PROTEA](https://github.com/frapercan/protea)
stack. Each sub-module implements the `ExperimentRunner` ABC from
[`protea-contracts`](https://github.com/frapercan/protea-contracts)
and registers via the `protea.runners` `entry_points` group.

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

## Documentation

Full Sphinx documentation in `docs/source/`. Each runner has its
own page documenting current status, the data shape it expects,
the artefacts it produces, and pointers to the active
implementation while the migration is pending.

## License

MIT. See `LICENSE`.
