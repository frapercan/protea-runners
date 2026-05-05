# protea-runners

Experiment runner plugins for the PROTEA stack. Each sub-module
implements the `ExperimentRunner` ABC from `protea-contracts`
and registers via `entry_points` group `protea.runners`.

## Sub-modules

| Sub-module | Runner | Status |
|------------|--------|--------|
| `protea_runners.lightgbm` | LightGBM reranker training | F2A.7 (currently placeholder; absorbs the existing protea-reranker-lab repo) |
| `protea_runners.knn` | KNN-only baseline (no reranker) | F2A.8 (placeholder) |
| `protea_runners.baseline` | Reference baselines for reproducibility | F2A.8 (placeholder) |
| `protea_runners.gnn` | R-GCN over GO-DAG (PROTEA-DL) | future, post-defensa |
| `protea_runners.retrieval_neural` | Neural retrieval reranker | future, post-defensa |

## How experiment runs are dispatched

1. The user submits an `ExperimentRun` row via PROTEA's API
   referencing a runner by name (e.g. `lightgbm`).
2. `protea-core` resolves the runner via
   `entry_points(group="protea.runners")["lightgbm"]`.
3. The runner gets a `spec`, `dataset_id`, and emits results
   that are persisted as a new `RerankerModel` (or equivalent)
   plus an `ExperimentRun` record.

## Roadmap

This is the F0 bootstrap (T0.13 of the PROTEA master plan v3).
The existing `protea-reranker-lab` repo migrates here as
`protea_runners.lightgbm` in F2A.7. The 888-LOC `staging.py`
and 400-LOC `runner.py` get refactored along the way (L1.1
to L1.6 of the master plan).

## Development

```bash
poetry install
poetry run pytest
poetry run ruff check .
poetry run mypy src tests
```
