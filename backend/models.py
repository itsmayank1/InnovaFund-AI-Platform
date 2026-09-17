from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    Date,
    Float
)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from database import Base


# ============================================================
# ORGANIZATION
# ============================================================

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    org_type = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    users = relationship(
        "User",
        back_populates="organization_rel"
    )


# ============================================================
# ROLE
# ============================================================

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    description = Column(String(255), nullable=True)
    permissions = Column(Text, nullable=True)


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(String(255), nullable=False)
    
    # Alias so code using user.hashed_password also works (Mayank, Member 2)
    @hybrid_property
    def hashed_password(self):
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value):
        self.password_hash = value

    role = Column(
        String(50),
        nullable=False,
        default="researcher",
        index=True
    )

    organization_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    is_active = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    organization_rel = relationship(
        "Organization",
        back_populates="users"
    )

    profile = relationship(
        "ResearchProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ============================================================
# RESEARCH PROFILE
# ============================================================

class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    title = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    technology_areas = Column(Text, nullable=True)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="profile"
    )

    interests = relationship(
        "ResearchInterest",
        back_populates="profile",
        cascade="all, delete-orphan"
    )

    keywords = relationship(
        "Keyword",
        back_populates="profile",
        cascade="all, delete-orphan"
    )

    publications = relationship(
        "Publication",
        back_populates="profile",
        cascade="all, delete-orphan"
    )

    patents = relationship(
        "Patent",
        back_populates="profile",
        cascade="all, delete-orphan"
    )


# ============================================================
# RESEARCH INTEREST
# ============================================================

class ResearchInterest(Base):
    __tablename__ = "research_interests"

    id = Column(Integer, primary_key=True, index=True)

    profile_id = Column(
        Integer,
        ForeignKey(
            "research_profiles.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    domain_name = Column(
        String(150),
        nullable=False,
        index=True
    )

    category = Column(
        String(100),
        nullable=True
    )

    weight = Column(
        Integer,
        default=1
    )

    profile = relationship(
        "ResearchProfile",
        back_populates="interests"
    )


# ============================================================
# KEYWORD
# ============================================================

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)

    profile_id = Column(
        Integer,
        ForeignKey(
            "research_profiles.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    keyword_name = Column(
        String(100),
        nullable=False,
        index=True
    )

    profile = relationship(
        "ResearchProfile",
        back_populates="keywords"
    )


# ============================================================
# PUBLICATION
# ============================================================

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)

    profile_id = Column(
        Integer,
        ForeignKey(
            "research_profiles.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    doi = Column(
        String(150),
        unique=True,
        nullable=True,
        index=True
    )

    title = Column(
        Text,
        nullable=False
    )

    authors = Column(
        Text,
        nullable=True
    )

    journal_or_venue = Column(
        String(255),
        nullable=True
    )

    publication_year = Column(
        Integer,
        nullable=True
    )

    citation_count = Column(
        Integer,
        default=0
    )

    external_source = Column(
        String(50),
        nullable=False
    )

    fetched_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    profile = relationship(
        "ResearchProfile",
        back_populates="publications"
    )


# ============================================================
# PATENT
# ============================================================

class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)

    profile_id = Column(
        Integer,
        ForeignKey(
            "research_profiles.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    patent_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    title = Column(
        Text,
        nullable=False
    )

    assignee = Column(
        String(255),
        nullable=True
    )

    filing_date = Column(
        Date,
        nullable=True
    )

    status = Column(
        String(50),
        default="Granted"
    )

    external_source = Column(
        String(50),
        nullable=False
    )

    fetched_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    profile = relationship(
        "ResearchProfile",
        back_populates="patents"
    )


# ============================================================
# SESSION
# ============================================================

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    session_token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    ip_address = Column(
        String(50),
        nullable=True
    )

    expires_at = Column(
        TIMESTAMP,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="sessions"
    )


# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    action = Column(
        String(100),
        nullable=False,
        index=True
    )

    resource = Column(
        String(100),
        nullable=False
    )

    details = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="audit_logs"
    )


# ============================================================
# NOTIFICATION
# ============================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="notifications"
    )


# ============================================================
# MILESTONE 2
# FUNDING SOURCE
# ============================================================

class FundingSource(Base):
    __tablename__ = "funding_sources"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False,
        unique=True,
        index=True
    )

    source_type = Column(
        String(100),
        nullable=False
    )

    country = Column(
        String(100),
        default="Global"
    )

    website = Column(
        String(255),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    opportunities = relationship(
        "FundingOpportunity",
        back_populates="source",
        cascade="all, delete-orphan"
    )


# ============================================================
# FUNDING OPPORTUNITY
# ============================================================

class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    source_id = Column(
        Integer,
        ForeignKey(
            "funding_sources.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    title = Column(
        String(255),
        nullable=False,
        index=True
    )

    agency = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    grant_amount = Column(
        Integer,
        nullable=False,
        default=0
    )

    currency = Column(
        String(10),
        default="USD"
    )

    deadline = Column(
        Date,
        nullable=False
    )

    status = Column(
        String(50),
        default="Open",
        index=True
    )

    # --------------------------------------------------------
    # Mayank / Grant Matching eligibility fields
    # --------------------------------------------------------

    research_domain = Column(
        String(150),
        nullable=False,
        index=True
    )

    career_stage = Column(
        String(100),
        nullable=False,
        default="Any"
    )

    eligible_geography = Column(
        String(150),
        nullable=False,
        default="Global"
    )

    funding_type = Column(
        String(100),
        nullable=False,
        default="Grant"
    )

    min_qualification = Column(
        String(100),
        nullable=True
    )

    external_link = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    source = relationship(
        "FundingSource",
        back_populates="opportunities"
    )

    criteria = relationship(
        "EligibilityCriteria",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )

    # --------------------------------------------------------
    # YOUR Recommendation Engine fields
    # --------------------------------------------------------

    domains = Column(
        Text,
        nullable=True
    )

    keywords = Column(
        Text,
        nullable=True
    )

    amount = Column(
        Float,
        nullable=True
    )

    past_success_rate = Column(
        Float,
        default=0.2
    )

    url = Column(
        String(500),
        nullable=True
    )


# ============================================================
# ELIGIBILITY CRITERIA
# ============================================================

class EligibilityCriteria(Base):
    __tablename__ = "eligibility_criteria"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    opportunity_id = Column(
        Integer,
        ForeignKey(
            "funding_opportunities.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    criteria_key = Column(
        String(100),
        nullable=False
    )

    criteria_value = Column(
        String(255),
        nullable=False
    )

    is_mandatory = Column(
        Boolean,
        default=True
    )

    weight = Column(
        Integer,
        default=25
    )

    opportunity = relationship(
        "FundingOpportunity",
        back_populates="criteria"
    )


# ============================================================
# YOUR MILESTONE 2
# RECOMMENDATION ENGINE
# ============================================================

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    researcher_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    opportunity_id = Column(
        Integer,
        ForeignKey(
            "funding_opportunities.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    score = Column(
        Float,
        nullable=False
    )

    domain_fit_score = Column(
        Float
    )

    deadline_score = Column(
        Float
    )

    amount_score = Column(
        Float
    )

    success_rate_score = Column(
        Float
    )

    eligible = Column(
        Integer,
        default=1
    )

    reasoning = Column(
        Text
    )

    generated_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    researcher = relationship("User")

    opportunity = relationship(
        "FundingOpportunity"
    )


# ============================================================
# YOUR MILESTONE 3
# PATENT RECORD
# ============================================================

class PatentRecord(Base):
    __tablename__ = "patent_records"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    assignee = Column(
        String,
        nullable=True
    )

    filing_date = Column(
        Date,
        nullable=True
    )

    classification = Column(
        String,
        nullable=True
    )

    technology_domain = Column(
        String,
        nullable=True
    )

    citation_count = Column(
        Integer,
        default=0
    )

    abstract = Column(
        String,
        nullable=True
    )


# ============================================================
# MAYANK - MILESTONE 3
# TECHNOLOGY INTELLIGENCE ENGINE
# ============================================================

class TechnologyDomain(Base):
    __tablename__ = "technology_domains"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True
    )

    category = Column(
        String(100),
        nullable=False,
        default="DeepTech"
    )

    patent_count = Column(
        Integer,
        default=0
    )

    publication_count = Column(
        Integer,
        default=0
    )

    growth_rate_pct = Column(
        Float,
        default=0.0
    )

    is_emerging = Column(
        Boolean,
        default=True,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    maturity = relationship(
        "TechnologyMaturity",
        back_populates="domain",
        uselist=False,
        cascade="all, delete-orphan"
    )

    competitors = relationship(
        "CompetitorActivity",
        back_populates="domain",
        cascade="all, delete-orphan"
    )


class TechnologyMaturity(Base):
    __tablename__ = "technology_maturities"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    domain_id = Column(
        Integer,
        ForeignKey(
            "technology_domains.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    lifecycle_stage = Column(
        String(50),
        nullable=False,
        default="Emerging"
    )

    trl_level = Column(
        Integer,
        default=3
    )

    maturity_score = Column(
        Float,
        default=65.0
    )

    adoption_velocity = Column(
        String(50),
        default="High"
    )

    commercial_readiness = Column(
        String(100),
        default="R&D Phase"
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    domain = relationship(
        "TechnologyDomain",
        back_populates="maturity"
    )


class CompetitorActivity(Base):
    __tablename__ = "competitor_activities"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    domain_id = Column(
        Integer,
        ForeignKey(
            "technology_domains.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    assignee_name = Column(
        String(200),
        nullable=False,
        index=True
    )

    patent_holdings = Column(
        Integer,
        default=1
    )

    market_share_pct = Column(
        Float,
        default=0.0
    )

    activity_status = Column(
        String(50),
        default="Active"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    domain = relationship(
        "TechnologyDomain",
        back_populates="competitors"
    )

UserProfile = ResearchProfile
ResearchDomain = ResearchInterest
TechnologyArea = TechnologyDomain
ResearchHistory = Keyword