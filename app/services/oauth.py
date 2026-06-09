from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.models.user import User
from app.services.auth import _issue_token_pair
from app.settings import settings

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def get_google_redirect(request: Request) -> str:
    redirect_uri = request.url_for("google_callback")
    result = await oauth.google.authorize_redirect(request, redirect_uri)
    return result.headers["location"]


async def handle_google_callback(request: Request, db: AsyncSession):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth failed - invalid or expired state",
        )

    user_info = token.get("userinfo")
    if not user_info or not user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from Google",
        )

    email: str = user_info["email"]
    full_name: str | None = user_info.get("name")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(email=email, full_name=full_name, is_google_user=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return await _issue_token_pair(user.id)
