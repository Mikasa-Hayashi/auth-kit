from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from auth_kit.redis_client import redis

RATE_LIMIT = 60
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else None
        if not ip:
            return await call_next(request)

        key = f"rate:{ip}"

        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, WINDOW_SECONDS)

        if count > RATE_LIMIT:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests - slow down"},
            )

        return await call_next(request)
