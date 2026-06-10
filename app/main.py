from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.settings import settings

app = FastAPI(title="auth-kit")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
