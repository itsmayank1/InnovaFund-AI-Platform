from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, date

# User & Auth Schemas
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field("researcher", pattern="^(researcher|startup_founder|innovation_manager|administrator)$")
    organization: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "researcher"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str
    email: str
    role: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Publication & Patent Schemas
class PublicationCreate(BaseModel):
    title: str
    authors: Optional[str] = None
    doi: Optional[str] = None
    journal_or_venue: Optional[str] = None
    publication_year: Optional[int] = None
    citation_count: int = 0
    external_source: str

class PublicationResponse(PublicationCreate):
    id: int
    fetched_at: datetime

    class Config:
        from_attributes = True

class PatentCreate(BaseModel):
    patent_number: str
    title: str
    assignee: Optional[str] = None
    filing_date: Optional[date] = None
    status: str = "Granted"
    external_source: str

class PatentResponse(PatentCreate):
    id: int
    fetched_at: datetime

    class Config:
        from_attributes = True

# Profile Schemas
class ProfileUpdate(BaseModel):
    title: Optional[str] = None
    bio: Optional[str] = None
    technology_areas: Optional[str] = None
    research_domains: Optional[List[str]] = None
    keywords: Optional[List[str]] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    bio: Optional[str] = None
    technology_areas: Optional[str] = None
    research_domains: List[str] = []
    keywords: List[str] = []
    publications: List[PublicationResponse] = []
    patents: List[PatentResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

# Audit Log & Notification Schemas
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Milestone 2: Member 2 Grant Matching Schemas
# ==========================================

class FundingOpportunityResponse(BaseModel):
    id: int
    title: str
    agency: str
    description: Optional[str] = None
    grant_amount: int
    currency: str = "USD"
    deadline: date
    status: str
    research_domain: str
    career_stage: str
    eligible_geography: str
    funding_type: str
    external_link: Optional[str] = None

    class Config:
        from_attributes = True


class GrantMatchRequest(BaseModel):
    researcher_id: Optional[int] = None
    research_domains: List[str] = Field(default_factory=list, description="List of research domains e.g. ['Artificial Intelligence', 'Biotechnology']")
    career_stage: Optional[str] = Field("Early-Career", description="Early-Career, Mid-Career, Senior/Lead, Startup/SME, Any")
    geography: Optional[str] = Field("Global", description="Global, US, EU, India, UK, Asia-Pacific")
    funding_types: List[str] = Field(default_factory=lambda: ["Grant", "Fellowship", "Accelerator"], description="Types of funding preferred")
    min_amount: Optional[int] = Field(0, description="Minimum funding amount USD")
    max_amount: Optional[int] = Field(None, description="Maximum funding amount USD")
    include_expired: bool = Field(False, description="Whether to include expired grants for testing")


class CriteriaMatchDetail(BaseModel):
    criterion: str
    status: str # MATCHED, PARTIAL, MISMATCHED, EXPIRED
    score: float # 0 to 100
    weight: float
    message: str


class EligibilityMatchResult(BaseModel):
    opportunity: FundingOpportunityResponse
    eligibility_status: str # ELIGIBLE, PARTIAL_MATCH, INELIGIBLE, EXPIRED
    is_eligible: bool # True if mandatory criteria pass
    overall_eligibility_score: float # Weighted eligibility score 0 to 100
    criteria_breakdown: List[CriteriaMatchDetail]
    rejection_reasons: List[str] = []


class GrantMatchResponse(BaseModel):
    total_evaluated: int
    total_eligible: int
    total_partial: int
    total_ineligible: int
    matched_grants: List[EligibilityMatchResult]


class MatchingRulesConfig(BaseModel):
    domain_weight: float = Field(35.0, description="Weight percentage for research domain match")
    career_stage_weight: float = Field(25.0, description="Weight percentage for career stage match")
    geography_weight: float = Field(25.0, description="Weight percentage for geographical eligibility match")
    funding_type_weight: float = Field(15.0, description="Weight percentage for funding type match")
    min_pass_threshold: float = Field(50.0, description="Minimum overall score threshold for eligibility")
    strict_geography_check: bool = Field(True, description="Strictly exclude grants if geography is restricted and mismatched")
    strict_deadline_check: bool = Field(True, description="Strictly mark grants past deadline as EXPIRED/INELIGIBLE")




# --- ADDED BY MEMBER 1 (Milestone 2) ---


class RecommendationOut(BaseModel):
    opportunity_id: int
    title: str
    agency: Optional[str]
    amount: Optional[float]
    deadline: Optional[datetime]
    url: Optional[str]
    score: float
    domain_fit_score: float
    deadline_score: float
    amount_score: float
    success_rate_score: float
    eligible: bool
    reasoning: str

    class Config:
        from_attributes = True

class GenerateRecommendationsRequest(BaseModel):
    researcher_id: int
    top_n: Optional[int] = 10
