from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class UserRole(str, enum.Enum):
    researcher = "researcher"
    startup_founder = "startup_founder"
    innovation_manager = "innovation_manager"
    administrator = "administrator"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.researcher)
    organization = Column(String, nullable=True)
    research_domain = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())