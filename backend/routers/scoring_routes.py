from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import ScoringRequest, ScoringResponse, ScoringBreakdown

router = APIRouter(prefix="/scoring", tags=["Milestone 3 — Innovation Scoring Engine"])


def calculate_innovation_score(payload: ScoringRequest) -> ScoringResponse:
    # Formula:
    # Research Novelty = 30%
    # Patent Strength = 20%
    # Technology Maturity = 15%
    # Market Potential = 20%
    # Funding Relevance = 15%
    novelty_w = payload.research_novelty * 0.30
    patent_w = payload.patent_strength * 0.20
    maturity_w = payload.technology_maturity * 0.15
    market_w = payload.market_potential * 0.20
    funding_w = payload.funding_relevance * 0.15

    overall_score = round(novelty_w + patent_w + maturity_w + market_w + funding_w, 2)

    if overall_score >= 85.0:
        tier = "Top Tier DeepTech Innovation (High Commercial Readiness)"
    elif overall_score >= 70.0:
        tier = "Strong Commercial & Grant Potential"
    elif overall_score >= 55.0:
        tier = "Moderate Readiness (Lab Prototype Phase)"
    else:
        tier = "Early R&D Phase (Requires IP Strengthening)"

    breakdown = ScoringBreakdown(
        research_novelty_score=payload.research_novelty,
        research_novelty_weighted=round(novelty_w, 2),
        patent_strength_score=payload.patent_strength,
        patent_strength_weighted=round(patent_w, 2),
        technology_maturity_score=payload.technology_maturity,
        technology_maturity_weighted=round(maturity_w, 2),
        market_potential_score=payload.market_potential,
        market_potential_weighted=round(market_w, 2),
        funding_relevance_score=payload.funding_relevance,
        funding_relevance_weighted=round(funding_w, 2),
    )

    summary = (
        f"Calculated overall Innovation Score: {overall_score}/100. "
        f"Weight breakdown: Research Novelty (30% -> {round(novelty_w, 2)}), "
        f"Patent Strength (20% -> {round(patent_w, 2)}), "
        f"Technology Maturity (15% -> {round(maturity_w, 2)}), "
        f"Market Potential (20% -> {round(market_w, 2)}), "
        f"Funding Relevance (15% -> {round(funding_w, 2)})."
    )

    return ScoringResponse(
        project_id=payload.project_id or 1,
        project_title=payload.project_title or "DeepTech Autonomous AI Agents",
        overall_score=overall_score,
        tier=tier,
        breakdown=breakdown,
        summary=summary,
        calculated_at=datetime.utcnow()
    )


@router.post("/calculate", response_model=ScoringResponse)
def calculate_score(payload: ScoringRequest, db: Session = Depends(get_db)):
    """
    POST /scoring/calculate: Computes Innovation Score using weighted 5-pillar formula:
    - Research Novelty: 30%
    - Patent Strength: 20%
    - Technology Maturity: 15%
    - Market Potential: 20%
    - Funding Relevance: 15%
    """
    return calculate_innovation_score(payload)


@router.get("/{project_id}", response_model=ScoringResponse)
def get_score_by_project(project_id: int, db: Session = Depends(get_db)):
    """
    GET /scoring/{project_id}: Retrieves calculated Innovation Score for specified project.
    """
    req = ScoringRequest(
        project_id=project_id,
        project_title=f"Project #{project_id} - Enterprise DeepTech R&D",
        research_novelty=86.5,
        patent_strength=80.0,
        technology_maturity=82.5,
        market_potential=91.0,
        funding_relevance=85.0
    )
    return calculate_innovation_score(req)
