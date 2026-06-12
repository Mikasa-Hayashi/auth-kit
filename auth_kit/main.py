from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from auth_kit.api.auth import router as auth_router
from auth_kit.api.users import router as users_router
from auth_kit.db.session import get_db
from auth_kit.middleware.rate_limit import RateLimitMiddleware
from auth_kit.redis_client import redis
from auth_kit.settings import settings

app = FastAPI(title="auth-kit")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    await db.execute(text("SELECT 1"))
    await redis.ping()
    return {"status": "ok"}
