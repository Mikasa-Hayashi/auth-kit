import logging
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.redis_client import redis
from app.schemas.token import TokenPair
from app.schemas.user import UserCreate
from app.settings import settings

logger = logging.getLogger(__name__)

BRUTE_FORCE_MAX_ATTEMPTS = 5
BRUTE_FORCE_BASE_DELAY = 30


async def register_user(data: UserCreate, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(email: str, password: str, db: AsyncSession) -> TokenPair:
    await _check_brute_force(email)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if (
        not user
        or not user.hashed_password
        or not verify_password(password, user.hashed_password)
    ):
        await _record_failed_login(email)
        logger.warning("Failed login attempt for email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled"
        )

    await _clear_failed_logins(email)
    return await _issue_token_pair(user.id)


async def refresh_tokens(refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_id: str = payload["sub"]
    stored = await redis.get(f"refresh:{user_id}")

    if stored != refresh_token:
        await redis.delete(f"refresh:{user_id}")
        logger.warning("Refresh token reuse detected for user_id: %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reused or expired",
        )

    return await _issue_token_pair(user_id)


async def logout_user(refresh_token: str) -> None:
    payload = decode_token(refresh_token)
    if not payload:
        return

    user_id: str = payload.get("sub", "")
    if user_id:
        await redis.delete(f"refresh:{user_id}")


async def _issue_token_pair(user_id: str) -> TokenPair:
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)

    ttl = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await redis.set(f"refresh:{user_id}", refresh, ex=int(ttl.total_seconds()))

    return TokenPair(access_token=access, refresh_token=refresh)


async def _check_brute_force(email: str) -> None:
    key = f"login_fail:{email}"
    attempts = await redis.get(key)
    if attempts and int(attempts) >= BRUTE_FORCE_MAX_ATTEMPTS:
        ttl = await redis.ttl(key)
        logger.warning("Account locked due to brute force for email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again in {ttl} seconds",
        )


async def _record_failed_login(email: str) -> None:
    key = f"login_fail:{email}"
    attempts = await redis.incr(key)
    if attempts == 1:
        await redis.expire(key, 3600)
    elif attempts >= BRUTE_FORCE_MAX_ATTEMPTS:
        delay = BRUTE_FORCE_BASE_DELAY * (2 ** (attempts - BRUTE_FORCE_MAX_ATTEMPTS))
        await redis.expire(key, int(delay))


async def _clear_failed_logins(email: str) -> None:
    await redis.delete(f"login_fail:{email}")
