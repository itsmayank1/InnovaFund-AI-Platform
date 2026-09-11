from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import FundingOpportunity, ResearchProfile
from recommendation_engine import compute_score

router = APIRouter(prefix="/recommendations", tags=["Milestone 2 — Funding Recommendation Engine"])

class GenerateRequest(BaseModel):
    researcher_id: int
    top_n: Optional[int] = 10

class RecommendationItem(BaseModel):
    opportunity_id: int
    title: str
    agency: Optional[str] = "Global Research Council"
    amount: Optional[float] = 500000
    deadline: Optional[str] = "2026-12-31"
    score: float
    eligible: bool
    reasoning: str
    url: Optional[str] = "https://seedfund.nsf.gov/"
    external_link: Optional[str] = "https://seedfund.nsf.gov/"

@router.get("/{researcher_id}", response_model=List[RecommendationItem])
def get_recommendations_by_researcher(researcher_id: int, db: Session = Depends(get_db)):
    return generate_recommendations(GenerateRequest(researcher_id=researcher_id, top_n=10), db)

@router.post("/generate", response_model=List[RecommendationItem])
def generate_recommendations(payload: GenerateRequest, db: Session = Depends(get_db)):
    opportunities = db.query(FundingOpportunity).all()
    if not opportunities:
        from services.grant_matching_service import seed_funding_opportunities_if_empty
        seed_funding_opportunities_if_empty(db)
        opportunities = db.query(FundingOpportunity).all()

    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == payload.researcher_id).first()
    profile_text = ""
    if profile:
        parts = []
        if profile.technology_areas:
            parts.append(profile.technology_areas)
        if profile.research_summary:
            parts.append(profile.research_summary)
        profile_text = " ".join(parts)
    if not profile_text:
        profile_text = "artificial intelligence machine learning quantum computing biotechnology clean energy"

    amounts = [opp.grant_amount for opp in opportunities if opp.grant_amount]
    min_amt = min(amounts) if amounts else 100000
    max_amt = max(amounts) if amounts else 2500000

    results = []
    for opp in opportunities:
        res = compute_score(profile_text, opp, min_amt, max_amt)
        link = getattr(opp, "external_link", None) or "https://seedfund.nsf.gov/"
        results.append(RecommendationItem(
            opportunity_id=opp.id,
            title=opp.title,
            agency=opp.agency or "Global Agency",
            amount=float(opp.grant_amount) if opp.grant_amount else 500000.0,
            deadline=opp.deadline.strftime("%Y-%m-%d") if opp.deadline else "2026-12-31",
            score=res["score"],
            eligible=res["score"] >= 45.0,
            reasoning=res["reasoning"],
            url=link,
            external_link=link
        ))

    results.sort(key=lambda x: x.score, reverse=True)
    return results[:payload.top_n]
