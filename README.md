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
| Tabular JSON – a list of flat objects, one per row | Reader available (0.2.0) |
| SQLite | Planned (0.5.0) |
| CSV | Planned |

Example of tabular JSON:

```json
[
  {"timestamp": "2026-10-01T08:00:00", "station": "north", "temperature": 12.5},
  {"timestamp": "2026-10-01T09:00:00", "station": "south", "temperature": null}
]
```

- Columns are all keys found in any row, in order of first appearance.
  A key missing from a row counts as a missing value.
- Nested objects or lists inside a row are not supported; the file is
  rejected with an error naming the row and column.

### Column types

Formats without a schema, such as JSON, get their column types inferred:

| Type | Inferred when all values are … |
|------|--------------------------------|
| `integer` | whole numbers |
| `number` | numbers, with at least one decimal |
| `boolean` | `true` / `false` |
| `date` | ISO 8601 dates, e.g. `2026-10-01` |
| `datetime` | ISO 8601 date-times, e.g. `2026-10-01T14:30:00Z` (date-only values allowed in the mix) |
| `string` | anything else, including mixed types |

Missing values are ignored when inferring, and mark the column as nullable.
Only ISO 8601 dates are recognised – ambiguous formats like `01/10/2026` stay
strings rather than being guessed.

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
