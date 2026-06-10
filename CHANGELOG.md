# Changelog

All notable changes to `protea-runners` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `protea_runners._base.StubRunner` shared base class for the
  contract-surface stub runners (Extract Superclass refactoring). Each
  runner now declares only its `name` and a per-method pointer at the
  active code path; the lifecycle signatures and the `NotImplementedError`
  construction live in one place.
- Sphinx documentation: a `quickstart` page, a `contract` page (the runner
  contract plus the shared stub base), and a consolidated `api` reference.
  Per-runner pages now render the inherited lifecycle methods via autodoc.
- `docs` GitHub Actions workflow that builds the HTML with warnings treated
  as errors and uploads the site as an artifact.
- `CHANGELOG.md` (this file) and an MIT `LICENSE`.

### Changed

- The CI matrix targets Python 3.12 only, matching the `>=3.12,<4.0` floor
  in `pyproject.toml` (the 3.10 and 3.11 legs failed at `poetry install`).
- Sphinx no longer mocks `protea-contracts`, `numpy` and `pyarrow`: they
  are real runtime dependencies, so the contract base and inherited
  lifecycle methods render with full type information.

## [0.0.1]

### Added

- Initial `protea.runners` entry-point pack with three contract-surface
  stub runners: `lightgbm`, `knn`, `baseline`. Each subclasses
  `protea_contracts.ExperimentRunner`, registers via entry points, and
  raises `NotImplementedError` until its migration lands (F2A.7 for
  LightGBM, F2C for KNN).
- Contract-compliance, payload round-trip, and discoverability test
  suites.

[Unreleased]: https://github.com/frapercan/protea-runners/compare/HEAD
[0.0.1]: https://github.com/frapercan/protea-runners/releases/tag/v0.0.1
