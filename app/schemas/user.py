from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    is_google_user: bool

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = None
