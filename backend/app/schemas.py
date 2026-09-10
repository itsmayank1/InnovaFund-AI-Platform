"""
Pydantic schemas — define the shape of data going in/out of the API.
Kept separate from SQLAlchemy models so we never accidentally expose
fields like hashed_password to the client.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.RESEARCHER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy object


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str          # user id
    role: UserRole
    exp: int
    type: str          # "access" or "refresh"
