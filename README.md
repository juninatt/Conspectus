# Conspectus

*Latin: "overview".*

Conspectus reads data that other applications produce – files and databases
in common formats – and presents it as interactive charts and tables. It is
source-agnostic: any project, in any language, can be connected by writing its
data in a supported format and listing it as a source.

> **Status:** early development. The backend is being set up.

## How it works

```
other projects → JSON / SQLite / CSV files
  → backend (FastAPI)
      sources.yaml → format readers → common dataset model → REST API
  → JSON over HTTP →
frontend (React + TypeScript): dataset list, tables, charts, dashboards
```

- Data sources are listed in `sources.yaml`.
- One reader per file format, all producing the same *dataset* model
  (columns, types, rows), so formats are interchangeable.
- Backend and frontend communicate only through the API.

## Tech stack

| Area     | Choice                                  |
|----------|-----------------------------------------|
| Backend  | Python, FastAPI, pytest                 |
| Frontend | TypeScript, React, Vite, Vitest         |
| Charts   | ECharts                                 |
| Tables   | TanStack Table                          |
| Storage  | SQLite locally, Postgres in the cloud   |

## Roadmap

1. Backend: JSON reader and API, explorable via `/docs`
2. Frontend: list datasets and show them as tables
3. Charts with selectable axis columns
4. Dashboards: saved layouts, theming, dark mode
5. CI (GitHub Actions), Docker, cloud deployment

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

Quality checks:

```bash
uv run pytest          # tests
uv run ruff check .    # lint
uv run ruff format .   # format
uv run mypy            # type check
```

## Repository layout

```
backend/    FastAPI application and tests
frontend/   React application and tests
docs/       Documentation, including the decision log
```

## Decisions

Key design decisions and their rationale are recorded in
[docs/decisions.md](docs/decisions.md).

## License

[MIT](LICENSE)
