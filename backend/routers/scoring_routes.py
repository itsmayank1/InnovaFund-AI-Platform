from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/scoring", tags=["Innovation Scoring Engine (Member 4)"])

class CalculateScorePayload(BaseModel):
    project_id: Optional[Union[int, str]] = "PRJ-001"
    project_title: Optional[str] = "DeepTech Innovation Project"
    research_novelty: float = Field(80.0, ge=0, le=100)
    patent_strength: float = Field(70.0, ge=0, le=100)
    technology_maturity: float = Field(60.0, ge=0, le=100)
    market_potential: float = Field(75.0, ge=0, le=100)
    funding_relevance: float = Field(70.0, ge=0, le=100)

def compute_score_dict(project_id: Union[int, str], title: str, novelty: float, patent: float, tech: float, market: float, funding: float) -> Dict[str, Any]:
    n_w = round(novelty * 0.3, 2)
    p_w = round(patent * 0.2, 2)
    t_w = round(tech * 0.15, 2)
    m_w = round(market * 0.2, 2)
    f_w = round(funding * 0.15, 2)
    total = round(n_w + p_w + t_w + m_w + f_w, 2)
    
    score_band = "Top Tier / High Readiness" if total >= 80 else ("Growth Candidate" if total >= 65 else "Early Stage Development")
    pid_val = int(project_id) if str(project_id).isdigit() else str(project_id)
    
    return {
        "project_id": pid_val,
        "project_title": title,
        "overall_score": total,
        "composite_score": total,
        "innovation_potential_score": total,
        "score_band": score_band,
        "recommendation": "Accelerate commercialization and initiate patent protection workflow." if total >= 75 else "Iterate R&D milestones.",
        "breakdown": {
            "research_novelty_weighted": n_w,
            "patent_strength_weighted": p_w,
            "technology_maturity_weighted": t_w,
            "market_potential_weighted": m_w,
            "funding_relevance_weighted": f_w
        },
        "pillars": {
            "research_novelty": {"value": novelty, "weight": 0.30, "weighted_score": n_w},
            "patent_strength": {"value": patent, "weight": 0.20, "weighted_score": p_w},
            "technology_maturity": {"value": tech, "weight": 0.15, "weighted_score": t_w},
            "market_potential": {"value": market, "weight": 0.20, "weighted_score": m_w},
            "funding_relevance": {"value": funding, "weight": 0.15, "weighted_score": f_w}
        },
        "derived_scores": {
            "defensibility": round((patent * 0.6) + (novelty * 0.4), 2),
            "commercial_readiness": round((market * 0.5) + (tech * 0.5), 2),
            "grant_competitiveness": round((funding * 0.6) + (novelty * 0.4), 2)
        },
        "explanation": f"Project '{title}' achieved a composite innovation score of {total}/100. Strong research novelty ({novelty}/100) and market potential ({market}/100) position it in the {score_band} band."
    }

@router.post("/calculate")
@router.post("/evaluate")
def calculate_score(payload: CalculateScorePayload):
    pid = payload.project_id or "PRJ-001"
    title = payload.project_title or f"Project {pid}"
    return compute_score_dict(
        project_id=pid,
        title=title,
        novelty=payload.research_novelty,
        patent=payload.patent_strength,
        tech=payload.technology_maturity,
        market=payload.market_potential,
        funding=payload.funding_relevance
    )

@router.get("/model/weights")
def get_scoring_weights():
    return {
        "weights": {
            "research_novelty": 0.30,
            "patent_strength": 0.20,
            "technology_maturity": 0.15,
            "market_potential": 0.20,
            "funding_relevance": 0.15
        },
        "description": "5-Pillar Weighted Innovation Scoring Engine"
    }

@router.get("/{project_id}")
def get_score_by_project_id(project_id: str):
    return compute_score_dict(
        project_id=project_id,
        title=f"Project {project_id}",
        novelty=81.0,
        patent=66.5,
        tech=58.0,
        market=74.0,
        funding=75.0
    )

@router.get("/{project_id}/history")
def get_score_history(project_id: str):
    return [
        {
            "evaluation_id": 1,
            "timestamp": "2026-03-01T10:00:00",
            "overall_score": 74.2,
            "score_band": "Growth Candidate"
        },
        {
            "evaluation_id": 2,
            "timestamp": "2026-03-25T14:30:00",
            "overall_score": 77.4,
            "score_band": "High Readiness"
        }
    ]
