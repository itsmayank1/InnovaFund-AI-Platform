"""
Innovation portfolio API (Member 4).

Serves the Innovation Manager dashboard with genuinely computed data: every
project in the scoring service's catalogue is scored through the weighted
five-pillar engine, then placed on the commercialization pipeline according to
its technology-readiness level and innovation band.

Endpoints
---------
GET /api/scoring/portfolio   scored portfolio + weights + portfolio average
GET /api/scoring/pipeline    the same projects grouped by pipeline stage
GET /api/scoring/project/{id}  full score detail for one catalogue project
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

# The scoring engine lives in the innovation-scoring-service package.
_CURRENT = os.path.dirname(os.path.abspath(__file__))
_SERVICE = os.path.abspath(os.path.join(_CURRENT, "..", "..", "innovation-scoring-service"))
if _SERVICE not in sys.path:
    sys.path.insert(0, _SERVICE)

router = APIRouter(prefix="/portfolio", tags=["Innovation Portfolio (Member 4)"])

PIPELINE_STAGES = ["ideation", "evaluation", "productization", "licensing", "startup"]

_SEED_PATH = os.path.join(_SERVICE, "data", "seed_projects.json")
_CACHE: Dict[str, Any] = {"projects": None}


def _load_seed_projects() -> List[Dict[str, Any]]:
    if _CACHE["projects"] is None:
        if not os.path.exists(_SEED_PATH):
            _CACHE["projects"] = []
        else:
            with open(_SEED_PATH, "r", encoding="utf-8") as handle:
                _CACHE["projects"] = json.load(handle)
    return _CACHE["projects"]


def _stage_for(score: float, trl: int) -> str:
    """
    Place a project on the commercialization pipeline.

    TRL decides how far a project has travelled toward market; the innovation
    score decides whether it is strong enough to move to the next stage at that
    readiness. A TRL-8 project with a weak score stays in licensing rather than
    becoming a spin-out candidate.

        TRL 1-3            ideation
        TRL 4-5            evaluation, or productization when the score is high
        TRL 6-7            productization, or licensing when the score is high
        TRL 8+             licensing, or startup when the score is high
    """
    if trl >= 8:
        return "startup" if score >= 85 else "licensing"
    if trl >= 6:
        return "licensing" if score >= 85 else "productization"
    if trl >= 4:
        return "productization" if score >= 80 else "evaluation"
    return "ideation"


def _score_project(project: Dict[str, Any]) -> Dict[str, Any]:
    """Run one catalogue project through the scoring engine."""
    from app.core.scoring import calculate_derived_scores, calculate_innovation_score
    from app.core.bands import get_score_band
    from app.core.weights import PRIMARY_PILLAR_WEIGHTS as PRIMARY_WEIGHTS

    pillars_input = {
        key: float(project.get(key, 0.0) or 0.0)
        for key in PRIMARY_WEIGHTS.keys()
    }

    score, pillar_detail = calculate_innovation_score(pillars_input)
    derived = calculate_derived_scores(pillars_input)
    band = get_score_band(score)

    readiness = derived.get("technology_readiness", {}) or {}
    trl = int(readiness.get("trl", 1))

    return {
        "project_id": project["project_id"],
        "title": project.get("title", project["project_id"]),
        "domain": project.get("domain", "Unclassified"),
        "overall_score": round(score, 2),
        "band": band,
        "trl": trl,
        "stage": _stage_for(score, trl),
        "components": {key: round(value, 2) for key, value in pillars_input.items()},
        "pillars": pillar_detail,
        "derived_scores": derived,
    }


def _scored_portfolio() -> List[Dict[str, Any]]:
    projects = [_score_project(p) for p in _load_seed_projects()]
    projects.sort(key=lambda p: p["overall_score"], reverse=True)
    return projects


@router.get("", summary="Scored innovation portfolio")
def get_portfolio() -> Dict[str, Any]:
    """Every catalogue project scored live by the weighted five-pillar model."""
    from app.core.weights import PRIMARY_PILLAR_WEIGHTS as PRIMARY_WEIGHTS

    projects = _scored_portfolio()
    if not projects:
        raise HTTPException(
            status_code=404,
            detail="No projects found in innovation-scoring-service/data/seed_projects.json",
        )

    average = sum(p["overall_score"] for p in projects) / len(projects)
    high_potential = [p for p in projects if p["overall_score"] >= 80]
    commercialization_ready = [
        p for p in projects if p["stage"] in ("productization", "licensing", "startup")
    ]

    return {
        "weights": dict(PRIMARY_WEIGHTS),
        "projects": projects,
        "portfolio_average": round(average, 1),
        "total_projects": len(projects),
        "high_potential_count": len(high_potential),
        "commercialization_ready_count": len(commercialization_ready),
    }


@router.get("/pipeline", summary="Portfolio grouped by commercialization stage")
def get_pipeline() -> Dict[str, Any]:
    """The scored portfolio arranged across the five pipeline stages."""
    projects = _scored_portfolio()
    grouped: Dict[str, List[Dict[str, Any]]] = {stage: [] for stage in PIPELINE_STAGES}
    for project in projects:
        grouped.setdefault(project["stage"], []).append(project)

    return {
        "stages": PIPELINE_STAGES,
        "grouped": grouped,
        "counts": {stage: len(items) for stage, items in grouped.items()},
    }


@router.get("/project/{project_id}", summary="Score detail for one project")
def get_project_detail(project_id: str) -> Dict[str, Any]:
    """Full pillar breakdown, derived scores and narrative for one project."""
    from app.core.scoring import generate_explanation
    from app.core.weights import PRIMARY_PILLAR_WEIGHTS as PRIMARY_WEIGHTS

    match: Optional[Dict[str, Any]] = next(
        (p for p in _load_seed_projects() if p["project_id"] == project_id), None
    )
    if match is None:
        raise HTTPException(status_code=404, detail=f"Unknown project: {project_id}")

    scored = _score_project(match)
    pillars_input = {key: float(match.get(key, 0.0) or 0.0) for key in PRIMARY_WEIGHTS}
    scored["explanation"] = generate_explanation(pillars_input, scored["overall_score"])
    scored["raw_metrics"] = match.get("raw_metrics", {})
    return scored
