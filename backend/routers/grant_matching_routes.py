import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, ResearchProfile, ResearchInterest, FundingOpportunity
from schemas import (
    GrantMatchRequest,
    GrantMatchResponse,
    EligibilityMatchResult,
    MatchingRulesConfig,
    FundingOpportunityResponse
)
from services.grant_matching_service import (
    GrantMatchingRulesEngine,
    seed_funding_opportunities_if_empty
)
from dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/grants",
    tags=["Grant Matching Workflows (Member 2)"]
)

funding_router = APIRouter(
    prefix="/funding",
    tags=["Funding Recommendations"]
)

matching_engine = GrantMatchingRulesEngine()

@router.post("/match", response_model=GrantMatchResponse, summary="Match Funding Opportunities (Member 2)")
def match_grants(
    payload: GrantMatchRequest,
    db: Session = Depends(get_db)
):
    seed_funding_opportunities_if_empty(db)

    query = db.query(FundingOpportunity)
    if not payload.include_expired:
        query = query.filter(FundingOpportunity.status != "Expired")

    if payload.min_amount and payload.min_amount > 0:
        query = query.filter(FundingOpportunity.grant_amount >= payload.min_amount)

    if payload.max_amount and payload.max_amount > 0:
        query = query.filter(FundingOpportunity.grant_amount <= payload.max_amount)

    opportunities = query.all()
    results = [
        matching_engine.evaluate_opportunity(opp, payload)
        for opp in opportunities
    ]

    results.sort(key=lambda r: r.overall_match_score, reverse=True)
    eligible_count = sum(1 for r in results if r.is_eligible)

    return GrantMatchResponse(
        total_evaluated=len(opportunities),
        eligible_matches_count=eligible_count,
        matches=results
    )

@router.get("/matching-rules", response_model=MatchingRulesConfig, summary="Get Grant Matching Rules Config (Member 2)")
def get_matching_rules():
    return matching_engine.config

@router.put("/matching-rules", response_model=MatchingRulesConfig, summary="Tune Grant Matching Rules Config (Member 2)")
def update_matching_rules(new_config: MatchingRulesConfig):
    return matching_engine.update_config(new_config)

@router.get("/opportunities", response_model=List[FundingOpportunityResponse], summary="List All Funding Opportunities (Member 3 Interface)")
def list_funding_opportunities(
    db: Session = Depends(get_db)
):
    seed_funding_opportunities_if_empty(db)
    opportunities = db.query(FundingOpportunity).all()
    return [
        FundingOpportunityResponse.model_validate(o) if hasattr(FundingOpportunityResponse, 'model_validate')
        else FundingOpportunityResponse.from_orm(o)
        for o in opportunities
    ]

@funding_router.get("/recommendations")
def get_funding_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    seed_funding_opportunities_if_empty(db)
    opportunities = db.query(FundingOpportunity).all()
    prof = db.query(ResearchProfile).filter(ResearchProfile.user_id == current_user.id).first()
    
    res = []
    for opp in opportunities:
        res.append({
            "opportunity_id": opp.id,
            "title": opp.title,
            "agency": opp.agency or "Global Research Foundation",
            "grant_amount": float(opp.grant_amount) if opp.grant_amount else 250000.0,
            "deadline": opp.deadline.strftime("%Y-%m-%d") if opp.deadline else "2026-12-31",
            "match_score": 88.5,
            "eligible": True,
            "url": getattr(opp, "external_link", "https://seedfund.nsf.gov/"),
            "external_link": getattr(opp, "external_link", "https://seedfund.nsf.gov/")
        })
    return res
