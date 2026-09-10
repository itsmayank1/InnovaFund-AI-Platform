from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    research_domains = Column(Text, nullable=True)   # comma-separated
    keywords = Column(Text, nullable=True)             # comma-separated
    bio = Column(Text, nullable=True)
    publications = Column(Text, nullable=True)          # comma-separated titles for now
    patents = Column(Text, nullable=True)
    technology_areas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="research_profile")