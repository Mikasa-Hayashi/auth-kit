# auth-kit

A reusable FastAPI authentication module. Install via pip and add to any FastAPI project in minutes.

## Features

- JWT access tokens (15 min) + refresh tokens (7 days) with rotation
- Google OAuth2 via authlib
- Redis-backed per-IP rate limiting (60 req/min)
- Brute-force protection — exponential backoff after 5 failed logins
- Async SQLAlchemy + Alembic migrations
- 90%+ test coverage

## Installation

```bash
pip install fastapi-auth-bundle
```

## Quick start (standalone server)

### 1. Start infrastructure

```bash
docker compose up -d
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in SECRET_KEY, DATABASE_URL, REDIS_URL
# Optionally: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start the server

```bash
uvicorn auth_kit.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API.

## Plugging into an existing FastAPI project

```python
from fastapi import FastAPI
from auth_kit.api.auth import router as auth_router
from auth_kit.api.users import router as users_router
from auth_kit.middleware.rate_limit import RateLimitMiddleware
from auth_kit.settings import settings

app = FastAPI()

app.add_middleware(RateLimitMiddleware)
app.include_router(auth_router)
app.include_router(users_router)
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | — | Create account |
| POST | `/auth/login` | — | Get token pair |
| POST | `/auth/refresh` | — | Rotate tokens |
| POST | `/auth/logout` | — | Invalidate refresh token |
| GET | `/auth/google` | — | Start Google SSO |
| GET | `/auth/google/callback` | — | Google SSO callback |
| GET | `/users/me` | ✓ | Get profile |
| PUT | `/users/me` | ✓ | Update profile |
| GET | `/health` | — | DB + Redis health check |

## Running tests

```bash
pytest --cov=auth_kit --cov-report=term-missing
```

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Postgres async URL | required |
| `REDIS_URL` | Redis URL | required |
| `SECRET_KEY` | JWT signing key (min 32 chars) | required |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `ALLOWED_ORIGINS` | CORS origins | `["*"]` |
| `DEBUG` | Enable SQL query logging | `false` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `""` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `""` |
