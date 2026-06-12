# auth-kit

A reusable FastAPI authentication module. Drop into any project via environment variables.

## Features

- JWT access tokens (15 min) + refresh tokens (7 days) with rotation
- Google OAuth2 via authlib
- Redis-backed per-IP rate limiting (60 req/min)
- Brute-force protection — exponential backoff after 5 failed logins
- Async SQLAlchemy + Alembic migrations
- 90%+ test coverage

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/Mikasa-Hayashi/auth-kit.git
cd auth-kit
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start infrastructure

```bash
docker compose up -d
```

### 3. Configure environment

```bash
cp .env.example .env
# Fill in SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API.

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

## Plugging into another project

1. Copy `app/core/`, `app/services/`, `app/middleware/`, `app/models/`, `app/schemas/` into your project
2. Add the routers to your `main.py`
3. Set the required env vars
4. Run `alembic upgrade head`

## Running tests

```bash
pytest --cov=app --cov-report=term-missing
```

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Postgres async URL | required |
| `REDIS_URL` | Redis URL | required |
| `SECRET_KEY` | JWT signing key | required |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `""` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `""` |
