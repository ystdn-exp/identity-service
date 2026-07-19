# Identity Service

A users + authentication service built with FastAPI. Handles signup, login,
email verification via OTP, password reset, and JWT access/refresh tokens.

## Running it locally

### With Docker (easiest)

```bash
cp .env.example .env
docker compose up --build
```

That's it - it brings up Postgres, Redis, runs migrations once (`migrate`
service), then starts the API (`web`), the Celery worker (`worker`), and the
beat scheduler (`beat`). Docs are at `http://localhost:8000/docs`.

The `.env.example` defaults (`DB_HOST=db`, `REDIS_HOST=redis`) already match
the docker network, so you shouldn't need to change anything for this path.

Emails (OTP codes for signup, email change, password reset) don't go to a
real inbox in dev - they're caught by Mailpit. Open
`http://localhost:8025` to read whatever was "sent".

If you change SQLAlchemy models later, generate the migration on your host
(not inside the container) and it'll get picked up next time `migrate` runs:

```bash
uv run alembic revision --autogenerate -m "some message"
```

### Without Docker

You'll need Postgres and Redis running and reachable yourself.

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Copy the env file and point it at your local Postgres/Redis:

   ```bash
   cp .env.example .env
   ```

   Change `DB_HOST` and `REDIS_HOST` from `db`/`redis` to `localhost`.

3. Run migrations (generate the first one if none exist yet):

   ```bash
   uv run alembic revision --autogenerate -m "init"
   uv run alembic upgrade head
   ```

4. Run the API:

   ```bash
   uv run fastapi dev app/main.py
   ```

5. Run the Celery worker and beat scheduler (needed for OTP emails and the
   daily unverified-user cleanup). Easiest to run both in one process for
   local dev:

   ```bash
   uv run celery -A app.core.celery_app worker -B --loglevel=info
   ```

## How it's organized

```
app/
├── main.py                  # builds the FastAPI app, wires middleware + routes
├── core/                    # infrastructure - not business logic
│   ├── settings.py          # env vars (pydantic-settings)
│   ├── database.py          # DB engine + sessions (async for the API, sync for Celery)
│   ├── celery_app.py        # celery app + beat schedule
│   ├── cors.py
│   ├── logging.py
│   ├── sentry.py
│   └── routes/routes_v1.py  # mounts every module's router under /api/v1
└── modules/
    ├── shared/               # code any module is allowed to depend on
    ├── auth/                 # signup, login, tokens, verification, password reset
    └── users/                # the user resource itself (profile, admin listing)
```

`core` is just plumbing - talking to the database, where settings come from,
the Celery instance, logging, error tracking, CORS. None of it knows
anything about users or auth specifically, and it shouldn't need to.

The actual product lives in `modules`, one folder per domain. Right now
that's just `auth` and `users`, but if this grows, each new domain gets its
own folder shaped the same way:

```
modules/<name>/
├── api/v1/
│   ├── router.py       # FastAPI endpoints
│   └── schemas.py      # request/response bodies
├── models.py            # SQLAlchemy tables (only if this module owns data)
├── service.py           # the actual logic - talks to the DB, raises errors
├── dependencies.py      # FastAPI Depends() wiring for this module
└── tasks/                # Celery jobs this module owns
```

Every module can import from `shared` - JWT encode/decode, password
hashing, OTP helpers, the enums, exceptions, cross-module permission checks
(`require_admin`, `require_self_or_admin`), the base SQLAlchemy model - but
not from each other. Anything two modules both need goes in `shared`
instead of getting copy-pasted or imported directly between them.

`auth` and `users` bend that rule a little (auth issues tokens for the
`User` model, which lives in `users`), but that's fine since the two are
tightly coupled by nature. It's not a pattern to repeat for domains that
don't actually need to know about each other.

## A few decisions worth knowing about

Login gives you an access token (10 minutes) and a refresh token (7 days).
Hitting `/auth/refresh` trades the refresh token for a new pair, and the
old one gets blacklisted in that same call - it's one-time use, not just a
renewal. Logout works the same way, blacklisting whatever access + refresh
tokens you send it. Nothing becomes invalid just by expiring; it has to be
blacklisted explicitly.

Signup, changing your email, and resetting your password all lean on the
same mechanism under the hood: generate an OTP code, email it through
Celery, verify it against what the user submits. `OTPType` just tags which
flow it's for, so improving the OTP logic once fixes it everywhere it's
used.

New users start out unverified and stay that way until they confirm the
code. A daily Celery job deletes anyone who's been sitting unverified for
2+ days, so an abandoned signup can't hold an email address hostage
forever.

One more thing worth knowing: `.env.example` is the real source of truth
for config, not this file - it already has sane defaults for local dev.
