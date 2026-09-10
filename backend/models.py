from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    org_type = Column(String(100), nullable=True) # University, Enterprise, Startup, Lab
    country = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    users = relationship("User", back_populates="organization_rel")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True) # researcher, startup_founder, innovation_manager, administrator
    description = Column(String(255), nullable=True)
    permissions = Column(Text, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="researcher", index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    organization_rel = relationship("Organization", back_populates="users")
    profile = relationship("ResearchProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    title = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    technology_areas = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")
    interests = relationship("ResearchInterest", back_populates="profile", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="profile", cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="profile", cascade="all, delete-orphan")
    patents = relationship("Patent", back_populates="profile", cascade="all, delete-orphan")


class ResearchInterest(Base):
    __tablename__ = "research_interests"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("research_profiles.id", ondelete="CASCADE"), nullable=False)
    domain_name = Column(String(150), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    weight = Column(Integer, default=1)

    profile = relationship("ResearchProfile", back_populates="interests")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("research_profiles.id", ondelete="CASCADE"), nullable=False)
    keyword_name = Column(String(100), nullable=False, index=True)

    profile = relationship("ResearchProfile", back_populates="keywords")


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("research_profiles.id", ondelete="SET NULL"), nullable=True)
    doi = Column(String(150), unique=True, nullable=True, index=True)
    title = Column(Text, nullable=False)
    authors = Column(Text, nullable=True)
    journal_or_venue = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)
    citation_count = Column(Integer, default=0)
    external_source = Column(String(50), nullable=False) # OpenAlex, CrossRef, Semantic Scholar
    fetched_at = Column(TIMESTAMP, server_default=func.now())

    profile = relationship("ResearchProfile", back_populates="publications")


class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("research_profiles.id", ondelete="SET NULL"), nullable=True)
    patent_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    assignee = Column(String(255), nullable=True)
    filing_date = Column(Date, nullable=True)
    status = Column(String(50), default="Granted") # Granted, Pending, Expired
    external_source = Column(String(50), nullable=False) # USPTO, Google Patents, The Lens
    fetched_at = Column(TIMESTAMP, server_default=func.now())

    profile = relationship("ResearchProfile", back_populates="patents")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False, index=True) # REGISTER, LOGIN, PROFILE_UPDATE, DATASET_SYNC
    resource = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="notifications")


# ==========================================
# Milestone 2: Funding Discovery & Matching Models
# ==========================================

class FundingSource(Base):
    __tablename__ = "funding_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    source_type = Column(String(100), nullable=False) # Government Grants, Research Councils, Innovation Funds, Accelerators, Venture Programs, Int'l Agencies
    country = Column(String(100), default="Global")
    website = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    opportunities = relationship("FundingOpportunity", back_populates="source", cascade="all, delete-orphan")


class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("funding_sources.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False, index=True)
    agency = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    grant_amount = Column(Integer, nullable=False, default=0) # Total funding amount in USD
    currency = Column(String(10), default="USD")
    deadline = Column(Date, nullable=False)
    status = Column(String(50), default="Open", index=True) # Open, Closed, Upcoming, Expired
    
    # Eligibility & Matching Metadata Fields (Collaborated with Member 3 & Member 1)
    research_domain = Column(String(150), nullable=False, index=True) # AI, BioTech, Climate, Quantum, CleanEnergy, etc.
    career_stage = Column(String(100), nullable=False, default="Any") # Early-Career, Mid-Career, Senior/Lead, Startup/SME, Any
    eligible_geography = Column(String(150), nullable=False, default="Global") # Global, US, EU, India, UK, Asia-Pacific
    funding_type = Column(String(100), nullable=False, default="Grant") # Grant, Fellowship, Accelerator, R&D Subsidy, Commercialization
    min_qualification = Column(String(100), nullable=True)
    external_link = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    source = relationship("FundingSource", back_populates="opportunities")
    criteria = relationship("EligibilityCriteria", back_populates="opportunity", cascade="all, delete-orphan")


class EligibilityCriteria(Base):
    __tablename__ = "eligibility_criteria"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("funding_opportunities.id", ondelete="CASCADE"), nullable=False)
    criteria_key = Column(String(100), nullable=False) # e.g. domain, career_stage, geography, funding_type, min_h_index
    criteria_value = Column(String(255), nullable=False)
    is_mandatory = Column(Boolean, default=True)
    weight = Column(Integer, default=25) # Weight out of 100

    opportunity = relationship("FundingOpportunity", back_populates="criteria")