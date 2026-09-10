import os
import sys
import logging

# Ensure backend directory is in python sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config import settings
from database import engine, SessionLocal, get_mongo_db
from models import Base, Role, User, Organization
from auth import hash_password
from routers import auth_routes, profile_routes, dataset_routes, admin_routes, grant_matching_routes, patent_routes
from routers import scoring_routes, commercialization_routes
from routers import technology_routes
from routers import trends_routes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create PostgreSQL database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Research Funding & Innovation Intelligence Platform API (Milestone 2)",
    version=settings.VERSION,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under standard API prefix
app.include_router(auth_routes.router, prefix=settings.API_PREFIX)
app.include_router(profile_routes.router, prefix=settings.API_PREFIX)
app.include_router(dataset_routes.router, prefix=settings.API_PREFIX)
app.include_router(admin_routes.router, prefix=settings.API_PREFIX)
app.include_router(grant_matching_routes.router, prefix=settings.API_PREFIX)
app.include_router(scoring_routes.router, prefix=settings.API_PREFIX)
app.include_router(commercialization_routes.router, prefix=settings.API_PREFIX)

# added by member 1
app.include_router(patent_routes.router, prefix=settings.API_PREFIX)
app.include_router(technology_routes.router, prefix=settings.API_PREFIX)
app.include_router(trends_routes.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def startup_db_seed():
    db = SessionLocal()
    try:
        # Seed default roles
        roles = [
            ("researcher", "Academic & Industry Scientists"),
            ("startup_founder", "Tech Entrepreneurs & DeepTech Founders"),
            ("innovation_manager", "University Tech Transfer & R&D Directors"),
            ("administrator", "Platform IT Administrators")
        ]

        for role_name, desc in roles:
            existing = db.query(Role).filter(Role.name == role_name).first()
            if not existing:
                db.add(Role(name=role_name, description=desc))

        # Seed default admin account
        admin = db.query(User).filter(
            User.email == "admin@researchsphere.ai"
        ).first()

        if not admin:
            admin = User(
                full_name="Platform Administrator",
                email="admin@researchsphere.ai",
                password_hash=hash_password("Admin@123456"),
                role="administrator",
                is_active=True
            )

            db.add(admin)

        db.commit()

    except Exception as e:
        logger.warning(f"Startup DB seed exception: {e}")

    finally:
        db.close()


@app.get("/")
def read_root():
    return {
        "status": "online",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    health = {
        "status": "ok",
        "postgres": "disconnected",
        "mongodb": "disconnected"
    }

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health["postgres"] = "connected"

    except Exception as e:
        health["postgres"] = f"error: {str(e)}"

    mongo = get_mongo_db()

    if mongo is not None:
        try:
            mongo.command("ping")
            health["mongodb"] = "connected"

        except Exception as e:
            health["mongodb"] = f"error: {str(e)}"

    return health


# --- ADDED BY MEMBER 1 (Milestone 2) ---

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db

from models import (
    ResearchProfile,
    Recommendation,
    FundingOpportunity,
    ResearchInterest
)

from schemas import (
    RecommendationOut,
    GenerateRecommendationsRequest,
    ProfileResponse as ResearchProfileResponse,
    GrantMatchRequest
)

from recommendation_engine import (
    compute_score,
    build_profile_text,
    get_opportunity_amount
)

from dependencies import get_current_user

from services.grant_matching_service import GrantMatchingRulesEngine


@app.delete("/profile")
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found."
        )

    db.delete(profile)
    db.commit()

    return {
        "message": "Research profile deleted successfully."
    }


@app.get(
    "/profiles",
    response_model=list[ResearchProfileResponse]
)
def list_profiles(
    db: Session = Depends(get_db),
):
    return db.query(ResearchProfile).all()


@app.get(
    "/profiles/domain/{domain}",
    response_model=list[ResearchProfileResponse]
)
def search_by_domain(
    domain: str,
    db: Session = Depends(get_db),
):
    profiles = db.query(ResearchProfile).filter(
        ResearchProfile.research_domains.ilike(f"%{domain}%")
    ).all()

    return profiles


@app.get(
    "/profiles/keyword/{keyword}",
    response_model=list[ResearchProfileResponse]
)
def search_by_keyword(
    keyword: str,
    db: Session = Depends(get_db),
):
    profiles = db.query(ResearchProfile).filter(
        ResearchProfile.keywords.ilike(f"%{keyword}%")
    ).all()

    return profiles


@app.post(
    "/recommendations/generate",
    response_model=list[RecommendationOut]
)
def generate_recommendations(
    req: GenerateRecommendationsRequest,
    db: Session = Depends(get_db)
):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == req.researcher_id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found for this researcher"
        )

    opportunities = db.query(FundingOpportunity).all()

    if not opportunities:
        raise HTTPException(
            status_code=404,
            detail="No funding opportunities available"
        )

    profile_text = build_profile_text(profile)

    amounts = [
        get_opportunity_amount(o)
        for o in opportunities
    ]

    amounts = [
        a for a in amounts
        if a
    ]

    min_amt, max_amt = (
        (min(amounts), max(amounts))
        if amounts
        else (0, 1)
    )

    db.query(Recommendation).filter(
        Recommendation.researcher_id == req.researcher_id
    ).delete()

    # --- Member 2 integration: real eligibility check ---

    matching_engine = GrantMatchingRulesEngine()

    interests = db.query(ResearchInterest).filter(
        ResearchInterest.profile_id == profile.id
    ).all()

    research_domains = [
        i.domain_name
        for i in interests
    ]

    if not research_domains:
        research_domains = [
            "Artificial Intelligence",
            "Biotechnology",
            "Climate & CleanEnergy"
        ]

    career_stage = "Early-Career"

    user_role = getattr(
        profile.user,
        "role",
        None
    )

    if user_role == "startup_founder":
        career_stage = "Startup/SME"

    elif user_role == "innovation_manager":
        career_stage = "Senior/Lead"

    match_request = GrantMatchRequest(
        researcher_id=req.researcher_id,
        research_domains=research_domains,
        career_stage=career_stage,
        geography="Global",
        funding_types=[
            "Grant",
            "Fellowship",
            "Accelerator"
        ],
        include_expired=False,
    )

    results = []

    for opp in opportunities:

        # Mayank's eligibility check
        eligibility_result = matching_engine.evaluate_opportunity(
            opp,
            match_request
        )

        eligible_value = (
            1
            if eligibility_result.is_eligible
            else 0
        )

        # Your recommendation engine
        scores = compute_score(
            profile_text,
            opp,
            min_amt,
            max_amt
        )

        rec = Recommendation(
            researcher_id=req.researcher_id,
            opportunity_id=opp.id,
            eligible=eligible_value,
            **scores,
        )

        db.add(rec)

        results.append(
            (opp, rec)
        )

    db.commit()

    ranked = sorted(
        results,
        key=lambda pair: pair[1].score,
        reverse=True
    )[:req.top_n]

    return [
        RecommendationOut(
            opportunity_id=opp.id,
            title=opp.title,
            agency=opp.agency,
            amount=opp.grant_amount,
            deadline=opp.deadline,
            url=opp.external_link,
            score=rec.score,
            domain_fit_score=rec.domain_fit_score,
            deadline_score=rec.deadline_score,
            amount_score=rec.amount_score,
            success_rate_score=rec.success_rate_score,
            eligible=bool(rec.eligible),
            reasoning=rec.reasoning,
        )
        for opp, rec in ranked
    ]


@app.get(
    "/recommendations/{researcher_id}",
    response_model=list[RecommendationOut]
)
def get_recommendations(
    researcher_id: int,
    db: Session = Depends(get_db)
):

    recs = (
        db.query(Recommendation)
        .filter(
            Recommendation.researcher_id == researcher_id
        )
        .order_by(
            Recommendation.score.desc()
        )
        .all()
    )

    if not recs:
        raise HTTPException(
            status_code=404,
            detail="No recommendations found. Call /generate first."
        )

    return [
        RecommendationOut(
            opportunity_id=r.opportunity.id,
            title=r.opportunity.title,
            agency=r.opportunity.agency,
            amount=r.opportunity.amount,
            deadline=r.opportunity.deadline,
            url=r.opportunity.url,
            score=r.score,
            domain_fit_score=r.domain_fit_score,
            deadline_score=r.deadline_score,
            amount_score=r.amount_score,
            success_rate_score=r.success_rate_score,
            eligible=bool(r.eligible),
            reasoning=r.reasoning,
        )
        for r in recs
    ]