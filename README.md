# Project Name

A small, focused web application built with **FastHTML**, **SQLAlchemy**, and **SQLite**, using **uv** for fast and reproducible Python tooling.

This project prioritizes:

- clarity over cleverness
- explicit data flow
- Pythonic code style
- minimal abstractions
- HTML-first rendering

---

## Tech Stack

- **Python** (3.12+)
- **FastHTML** — server-side HTML rendering with a lightweight, explicit model
- **SQLAlchemy** — ORM + Core for database access
- **SQLite** — simple, file-based database (great for local dev and small deployments)
- **uv** — dependency management and virtual environments

---

## Project Structure

```text
.
├── app/
│   ├── main.py            # FastHTML app entrypoint
│   ├── db.py              # Engine + session setup
│   ├── models.py          # SQLAlchemy ORM models
│   ├── views/             # Route handlers / page logic
│   ├── templates/         # HTML templates (FastHTML)
│   └── services/          # Domain / business logic
│
├── tests/
│   └── ...
│
├── .env.example
├── README.md
├── CONTRIBUTING.md
└── pyproject.toml

## Running with Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

The app is available at `http://localhost:5001`.

Database data is persisted in a named Docker volume mounted at `/var/lib/ty` in the container.
