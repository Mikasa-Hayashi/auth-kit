from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.token import RefreshRequest, TokenPair
from app.schemas.user import LoginRequest, UserCreate, UserResponse
from app.services import auth as auth_service
from app.services.oauth import get_google_redirect, handle_google_callback

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    user = await auth_service.register_user(data, db)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    return await auth_service.login_user(data.email, data.password, db)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshRequest) -> TokenPair:
    return await auth_service.refresh_tokens(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(data: RefreshRequest) -> None:
    await auth_service.logout_user(data.refresh_token)


@router.get("/google")
async def google_login(request: Request) -> RedirectResponse:
    redirect_url = await get_google_redirect(request)
    return RedirectResponse(redirect_url)


@router.get("/google/callback", name="google_callback", response_model=TokenPair)
async def google_callback(
    request: Request, db: AsyncSession = Depends(get_db)
) -> TokenPair:
    return await handle_google_callback(request, db)
