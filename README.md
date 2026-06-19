# Nursing Home Management System

REST API for managing a chain of boarding houses: rooms, beds, residents, and advance bookings. Built as a university project at МГТУ КФ.

## Stack

**Python 3.11** · **FastAPI** · **SQLAlchemy 2.0** · **PostgreSQL 15** · **Alembic** · **Docker Compose**

## Architecture

The project is organized into three layers that correspond to the classic separation of concerns for a web API. Routers in `app/routers/` handle HTTP and delegate to the database through SQLAlchemy sessions. Models in `app/models/` use the SQLAlchemy 2.0 typed API — every column is declared with `Mapped[T]` and `mapped_column()`, which gives full type-checker coverage without runtime overhead. Schemas in `app/schemas/` are Pydantic v2 models and are split into *request* and *response* variants so the shapes of incoming and outgoing data are always explicit.

Database sessions are provided to route handlers via `get_db`, a FastAPI dependency that opens a session at the start of a request and closes it unconditionally in a `finally` block. Database migrations are managed with Alembic.

## Domain model

A **Pansionat** (boarding house) contains **Rooms**, each of which belongs to a **RoomType** that defines the nightly rate. Each room can have one or more **Beds**. The two main operational objects are **Residents** — people currently living in the facility — and **Bookings** — advance reservations for a specific bed.

The two business rules worth noting: first, a bed cannot have overlapping bookings, and a booking cannot be converted to a check-in if the bed is occupied — the backend enforces both with explicit date-range overlap queries rather than relying on unique constraints alone. Second, the `check_in_price` is copied from the room type at the moment of check-in and never changes afterward, so editing a room type's rate does not affect existing residents.

## API

All routes are prefixed by resource name and follow REST conventions. The full interactive spec is available at `/docs` (Swagger UI) while the server is running.

| Prefix | Coverage |
|---|---|
| `/pansionats` | CRUD for boarding houses |
| `/room-types` | CRUD for room categories and nightly rates |
| `/rooms` | CRUD for rooms, filtered by pansionat |
| `/beds` | CRUD + active/repair status toggle |
| `/residents` | Check-in, edit, extend stay, check-out, history |
| `/bookings` | Create, edit, cancel, convert to check-in |

## Running locally

```bash
docker compose up --build
```

The API starts at `http://localhost:8000`. A simple frontend for manual testing is served from `/static/index.html`.

To populate the database with generated test data:

```bash
docker compose exec app python seed_data.py
```
