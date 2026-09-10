"""
Week 1 deliverable: User & Role schema.

Design decisions:
- Roles are a fixed Python Enum (4 roles only, per the project spec) rather than
  a separate roles table, because the role set is small and unlikely to change
  often. This keeps RBAC checks fast (no extra join needed).
- Password is NEVER stored in plain text — only hashed_password (bcrypt hash).
- is_active supports the "deactivate account" feature from Week 4.
- oauth_provider / oauth_id support Google OAuth2 login from Week 4, while still
  allowing normal email/password users (both fields nullable).
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class UserRole(str, enum.Enum):
    RESEARCHER = "researcher"
    STARTUP_FOUNDER = "startup_founder"
    INNOVATION_MANAGER = "innovation_manager"
    ADMINISTRATOR = "administrator"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)

    # Nullable because OAuth-only users won't have a local password.
    hashed_password = Column(String, nullable=True)

    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.RESEARCHER)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # OAuth2 fields (Week 4)
    oauth_provider = Column(String, nullable=True)  # e.g. "google"
    oauth_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RefreshToken(Base):
    """
    Stores issued refresh tokens so they can be revoked (e.g. on logout or
    password change) instead of relying purely on JWT expiry.
    """
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
