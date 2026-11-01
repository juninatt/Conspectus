# Conspectus

*Latin: "overview".*

Conspectus reads data that other applications produce – files and databases
in common formats – and presents it as interactive charts and tables. It is
source-agnostic: any project, in any language, can be connected by writing its
data in a supported format and listing it as a source.

> **Status:** early development. See the [roadmap](docs/roadmap.md) and the
> [changelog](CHANGELOG.md).

## How it works

```
producing applications → JSON / SQLite / CSV files
  → backend (FastAPI)
      1. sources are listed in sources.yaml
      2. one reader per file format
      3. every reader returns the same dataset model (columns, types, rows)
      4. REST API: /sources, /datasets/{id}
  → JSON over HTTP →
frontend (React + TypeScript): dataset list, tables, charts, dashboards
```

- Conspectus only **reads** data. Producers don't need to know it exists –
  they just write a file.
- Readers are interchangeable: adding a format means adding a reader, nothing
  else changes.
- Backend and frontend communicate only through the API.

## Supported data formats

| Format | Status |
|--------|--------|
| Tabular JSON – a list of flat objects, one per row | Planned (0.2.0) |
| SQLite | Planned (0.5.0) |
| CSV | Planned |

Example of tabular JSON:

```json
[
  {"date": "2026-10-01", "query": "first", "score": 0.82},
  {"date": "2026-10-02", "query": "second", "score": 0.67}
]
```

Arbitrarily nested JSON is not supported.

## Tech stack

| Area     | Choice                                  |
|----------|-----------------------------------------|
| Backend  | Python, FastAPI, pytest                 |
| Frontend | TypeScript, React, Vite, Vitest         |
| Charts   | ECharts                                 |
| Tables   | TanStack Table                          |
| Storage  | SQLite locally, Postgres in the cloud   |
| Tooling  | uv, ruff, mypy (strict)                 |

## Getting started

### Backend

Requires [uv](https://docs.astral.sh/uv/) (it installs the right Python
version automatically).

```bash
cd backend
uv sync                                  # create environment, install deps
uv run fastapi dev src/conspectus/main.py
```

The API is then available at <http://localhost:8000>, with interactive
documentation at <http://localhost:8000/docs>.

## Development

All commands run from `backend/`. All checks must pass before a change is
committed.

```bash
uv run pytest            # tests
uv run ruff check .      # lint
uv run ruff format .     # format
uv run mypy              # type check (strict)
uv add <package>         # add a runtime dependency
uv add --dev <package>   # add a development dependency
```

### Conventions

- **Commits** follow [Conventional Commits](https://www.conventionalcommits.org/)
  in the imperative mood. Scopes: `backend`, `frontend`, `ci`, `docker`;
  no scope for repository-wide changes.
- **Versioning** follows [Semantic Versioning](https://semver.org/). The
  version is defined only in `backend/pyproject.toml`; the application reads
  it from the package metadata.
- **Changes** are recorded under *Unreleased* in [CHANGELOG.md](CHANGELOG.md)
  and moved to a version section on release. Each release is tagged `vX.Y.Z`.
- **Decisions** with lasting impact are recorded in
  [docs/decisions.md](docs/decisions.md).
- **Code organisation:** packages are split by responsibility (`api/`,
  `readers/`, `models/` …) while staying idiomatic Python.

## Repository layout

```
backend/    FastAPI application and tests
frontend/   React application and tests (from 0.6.0)
docs/       Roadmap and decision log
```

## License

[MIT](LICENSE)
