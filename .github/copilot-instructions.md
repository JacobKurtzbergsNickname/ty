# Reference sources

For all FastHTML-related questions, consult `fasthtml-llms-ctx.txt` first. This file is the primary reference for FastHTML idioms, patterns, and best practices.

If further information is needed (e.g., for Python, SQLAlchemy, or general Microsoft/VS Code topics), use the Microsoft Learn MCP server as the secondary source.


# Static analysis requirements

All generated code must satisfy:
- **Pylance** in `typeCheckingMode = strict`
- **Pylint** with the project configuration

Before proposing final code:
- Ensure no obvious Pylance errors (unknown types, incompatible return types).
- Avoid common Pylint issues:
  - unused imports
  - unused variables
  - overly broad exception catches
  - missing docstrings for public functions
  - too many branches in a single function

If code would violate Pylint or Pylance rules:
- Refactor proactively
- Add precise type hints
- Split logic into smaller functions

# .github/copilot-instructions.md
# Copilot instructions for this repo (FastHTML + SQLAlchemy + SQLite + uv)
#
# Goal: generate *Pythonic*, readable code that matches FastHTML’s HTML-first, HTMX-friendly approach,
# and uses SQLAlchemy 2.x idioms with safe session lifecycles.

## Stack facts (do not “invent” alternatives)
- Web framework: **FastHTML** (HTML-first, server-rendered hypermedia). FastHTML is *not* FastAPI syntax. :contentReference[oaicite:0]{index=0}
- Runtime: FastHTML uses `serve()` (uvicorn runner) and you generally **don’t need** `if __name__ == "__main__"`. :contentReference[oaicite:1]{index=1}
- Tooling: **uv** for env + deps; prefer `uv sync` and `uv run …`. `uv run` auto-locks/syncs before running. :contentReference[oaicite:2]{index=2}
- DB: **SQLite** via **SQLAlchemy ORM**.

## Core style goals (Pythonic)
- Prefer clarity over cleverness; “explicit is better than implicit”.
- Prefer **small functions** and **plain modules** over large classes.
- Use type hints for public functions and non-trivial data structures.
- Avoid over-abstraction (no generic repositories unless justified by repetition).
- Keep I/O at the edges (HTTP + DB); keep business logic in service functions.

## FastHTML rules (HTML-first, HTMX-friendly)
- Use `from fasthtml.common import *` at the top of FastHTML modules. :contentReference[oaicite:3]{index=3}
- App setup pattern:
  - `app, rt = fast_app()`
  - use `@rt` or `@rt("/path")` decorators for routes. :contentReference[oaicite:4]{index=4}
- Return **FastTags / FT components** (e.g., `Div(...)`, `P(...)`, `H1(...)`) or tuples of components.
  - Remember: HTMX requests receive partials; normal requests get a full doc. :contentReference[oaicite:5]{index=5}
- When you need a page title + layout, prefer FastHTML’s helpers (e.g., `Titled`) instead of hand-rolling repeated layout. :contentReference[oaicite:6]{index=6}
- Do not propose React/Vue/Svelte integration; FastHTML is compatible with vanilla JS/web components, not those frameworks. :contentReference[oaicite:7]{index=7}
- Keep routes “thin”:
  - parse/validate inputs
  - call service functions
  - render FT components

## SQLAlchemy 2.x rules (session lifecycle + idioms)
- Scope `Engine` and `sessionmaker` at module/global level (factories are safe to reuse). :contentReference[oaicite:8]{index=8}
- Use context-managed sessions:
  - `with Session() as session:` and commit/close deterministically (or use a helper that does this).
  - Prefer explicit transactions (`with session.begin(): …`) where appropriate.
- Keep DB usage out of view functions when logic is non-trivial; use `services/` (or `app/services/`) functions.
- Prefer SQLAlchemy 2.x patterns:
  - `select(...)`, `session.execute(...)`, `scalar_one()/scalars()`
  - avoid legacy query patterns when possible.

## uv workflow rules (commands, scripts, docs)
- Do not assume `pip`, `poetry`, or `pipenv`. Prefer `uv` flows. :contentReference[oaicite:9]{index=9}
- When suggesting commands:
  - install/sync: `uv sync`
  - run: `uv run python -m <module>` (or `uv run pytest`, etc.)
- Don’t invent script names; prefer those already present in `pyproject.toml` / README.

## uv scripts and commands

This project uses **uv**. Scripts are defined using the **standard Python entry-point mechanism** under `[project.scripts]` in `pyproject.toml`. There is no uv-specific `tool.uv.scripts` table. When referring to or adding runnable commands, always use `uv run <script>` and assume uv will automatically create/sync the virtual environment. Do not suggest `pip`, `poetry`, `pipenv`, or manual venv activation. Only reference scripts that are actually defined in `pyproject.toml`.
Please note: To install entry points, set `tool.uv.package = true` or define a `build-system`!

## File organization (preferred)
- `app/main.py`: app entrypoint, routes wire-up, `serve()`
- `app/db.py`: engine + sessionmaker + session helpers
- `app/models.py`: SQLAlchemy models
- `app/services/*.py`: business logic
- `app/views/*.py`: route handlers (thin)
- `tests/`: pytest tests

(If the repo already uses a different structure, follow the repo, but keep the “thin views / fat services” boundary.)

## Error handling
- Fail clearly. Return user-safe messages; do not leak internals.
- Prefer consistent error response patterns for HTMX:
  - return an error partial (e.g., `Div(..., cls="error")`) rather than raising raw exceptions to users.

## What to output when asked to implement a feature
1) A short plan (files to change, new functions, data flow).
2) Then code changes in small, reviewable chunks.
3) Include at least one test when logic is non-trivial.

## Anti-patterns (avoid)
- Adding async “because modern” (don’t unless required).
- Massive route functions with DB + HTML + business rules mixed.
- Hidden global sessions or long-lived sessions.
- Unnecessary class hierarchies or “enterprise patterns”.

## When uncertain
- Prefer the documented FastHTML route/serve patterns and FT returns. :contentReference[oaicite:10]{index=10}
- Prefer SQLAlchemy’s sess
