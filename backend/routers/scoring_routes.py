from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/scoring", tags=["Innovation Scoring Engine (Member 4)"])

class CalculateScorePayload(BaseModel):
    project_id: Optional[int] = 1
    project_title: Optional[str] = "DeepTech Innovation Project"
    research_novelty: float = Field(..., ge=0, le=100)
    patent_strength: float = Field(..., ge=0, le=100)
    technology_maturity: float = Field(..., ge=0, le=100)
    market_potential: float = Field(..., ge=0, le=100)
    funding_relevance: float = Field(..., ge=0, le=100)

@router.post("/calculate")
@router.post("/evaluate")
def calculate_score(payload: CalculateScorePayload):
    n_w = round(payload.research_novelty * 0.3, 2)
    p_w = round(payload.patent_strength * 0.2, 2)
    t_w = round(payload.technology_maturity * 0.15, 2)
    m_w = round(payload.market_potential * 0.2, 2)
    f_w = round(payload.funding_relevance * 0.15, 2)
    
    total = round(n_w + p_w + t_w + m_w + f_w, 2)
    
    return {
        "project_id": payload.project_id or 1,
        "project_title": payload.project_title,
        "overall_score": total,
        "innovation_potential_score": total,
        "breakdown": {
            "research_novelty_weighted": n_w,
            "patent_strength_weighted": p_w,
            "technology_maturity_weighted": t_w,
            "market_potential_weighted": m_w,
            "funding_relevance_weighted": f_w
        },
        "score_band": "Top Tier / High Readiness" if total >= 80 else "Growth Candidate",
        "pillars": {
            "research_novelty": payload.research_novelty,
            "patent_strength": payload.patent_strength,
            "technology_maturity": payload.technology_maturity,
            "market_potential": payload.market_potential,
            "funding_relevance": payload.funding_relevance
        }
    }

@router.get("/{project_id}")
def get_score_by_project_id(project_id: int):
    return {
        "project_id": project_id,
        "project_title": f"DeepTech Project #{project_id}",
        "overall_score": 81.75,
        "score_band": "Top Tier / High Readiness",
        "breakdown": {
            "research_novelty_weighted": 27.0,
            "patent_strength_weighted": 16.0,
            "technology_maturity_weighted": 10.5,
            "market_potential_weighted": 17.0,
            "funding_relevance_weighted": 11.25
        }
    }
