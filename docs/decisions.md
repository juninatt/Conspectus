# Decision log

Important decisions and why they were made. Newest entries last.
Each entry: date, decision, context/rationale. Superseded decisions are kept
and marked as such rather than deleted.

---

## 001 – Separate backend and frontend (2026-10-28)
**Decision:** Python + FastAPI backend and TypeScript + React (Vite) frontend,
in one repository under `backend/` and `frontend/`. They communicate only
through an HTTP/JSON API.

**Why:** Each side uses the best tool for its job, and the API boundary keeps
them independently testable and replaceable. One repository keeps CI, Docker
and documentation in one place. Streamlit was rejected: fast to start, but it
couples UI and data logic and would require a rewrite to reach the intended
quality.

## 002 – ECharts for charts, TanStack Table for tables (2026-10-28)
**Decision:** Use ECharts and TanStack Table in the frontend.

**Why:** ECharts covers a wide range of interactive chart types with good
performance on larger datasets. TanStack Table is headless, so sorting,
filtering and pagination logic comes for free while styling stays fully under
our control.

## 003 – Read data, don't receive it (2026-10-28)
**Decision:** Conspectus reads files and databases that other projects
produce. There is no live push or ingestion API.

**Why:** Keeps the other projects unaware of Conspectus – they only need to
write a file. Simpler to build, test and reason about.

## 004 – Tabular JSON first, then SQLite, then CSV (2026-10-28)
**Decision:** First supported format is a JSON list of flat objects (one per
row). SQLite follows, then CSV. Nested JSON is out of scope for now.

**Why:** Tabular JSON is trivial to produce from virtually any language and maps
directly to a table. Adding SQLite second proves that readers are
interchangeable behind a common dataset model.

## 005 – SQLite locally, Postgres later (2026-10-28)
**Decision:** Store Conspectus' own metadata (e.g. saved dashboards) in SQLite
while running locally; move to Postgres when deploying to the cloud.

**Why:** SQLite needs no server and is ideal for local development. Using a
standard SQL access layer keeps the later switch small.

## 006 – MIT license (2026-10-28)
**Decision:** The project is released under the MIT license.

**Why:** Short, widely understood and permissive. It makes clear that the code
may be read, run and reused, which suits a public portfolio project.

## 007 – Source-agnostic by design (2026-10-28)
**Decision:** Conspectus has no knowledge of any specific data producer. All
sources are described in configuration, and code, docs and sample data stay
generic.

**Why:** The application should be easy to connect to many different
producers. Coupling it to particular projects would leak their assumptions
into the data model and make it harder to reuse.

## 008 – Python tooling: uv, ruff, mypy (2026-10-28)
**Decision:** Manage the backend environment and dependencies with uv, lint
and format with ruff, and type check with mypy in strict mode from the start.
The package uses the `src/` layout.

**Why:** uv's lock file gives identical environments locally, in CI and in
Docker. ruff replaces several tools with one fast one. Strict typing from day
one is much cheaper than adding it later, and the dataset model – columns and
types – is the core of the application. The `src/` layout makes tests run
against the installed package, which catches packaging mistakes early.

## 009 – Semantic versioning with changelog and tags (2026-11-01)
**Decision:** Plan and release work as Semantic Versioning milestones
(`MAJOR.MINOR.PATCH`). Each release is recorded in `CHANGELOG.md` and marked
with an annotated git tag `vX.Y.Z`. The version number is defined once, in
`backend/pyproject.toml`.

**Why:** Versions give each milestone a clear scope and a point in history
that can be found, compared and rolled back to. A changelog tells readers
what changed without digging through commits. A single source for the version
number prevents it from drifting between files. Before 1.0.0 the API may
still change; 1.0.0 marks the first complete release for local use.

The SQLite reader is planned before the frontend so that the dataset model is
proven against two formats before anything is built on top of it.

## 010 – Dataset model and column type inference (2026-11-02)
**Decision:** Every reader returns a `Dataset`: a list of columns (name, type,
nullable) and rows keyed by column name. Column types are `string`,
`integer`, `number`, `boolean`, `date` and `datetime`. For formats without a
schema the type is inferred from the values:
- missing values (`null` or absent keys) are ignored and make the column
  nullable; a column with only missing values is `string`
- dates are recognised only in ISO 8601 form
- a mix of integers and decimals is `number`; a mix of dates and date-times
  is `datetime`; any other mix is `string`
- nested objects or lists are rejected with an error

Readers receive their settings when created and expose a single `read()`
method, so all formats share one interface.

**Why:** Rows keyed by name match both tabular JSON and how the frontend
table consumes data. Integers and decimals are kept apart because they are
used differently (counts and ids versus measurements). Accepting only ISO
dates avoids silently misreading ambiguous formats such as `01/10/2026`.
Falling back to `string` keeps imperfect data viewable instead of failing
the whole dataset, while nested data is rejected explicitly because it is
out of scope rather than something to guess at. Mixing time-zone-aware and
naive date-times also falls back to `string`, since they cannot be compared.

**Known limitation:** files are read fully into memory. This is fine for
tens of thousands of rows; streaming can be added behind the same reader
interface if needed. Per-column type overrides are planned for the source
configuration in 0.3.0.
