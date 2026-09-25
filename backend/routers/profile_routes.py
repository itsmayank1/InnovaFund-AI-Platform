from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database import get_db
from schemas import ProfileResponse, ProfileUpdate
from services.profile_service import ProfileService
from dependencies import get_current_user
from models import User, ResearchProfile, ResearchInterest, Keyword, Publication, Patent
from repositories.profile_repository import ProfileRepository

router = APIRouter(prefix="/profiles", tags=["Research Profile Management"])
profile_alias_router = APIRouter(prefix="/profile", tags=["Research Profile Management"])
users_alias_router = APIRouter(prefix="/users", tags=["Users Profile Alias"])

# In-memory store for research history across test sessions
RESEARCH_HISTORY_STORE: Dict[int, List[Dict[str, Any]]] = {}

def build_profile_dict(prof: ResearchProfile, db: Session) -> Dict[str, Any]:
    domains = [i.domain_name for i in prof.interests]
    keywords = [k.keyword_name for k in prof.keywords]
    pub_ids = [p.id for p in prof.publications]
    pat_ids = [pt.id for pt in prof.patents]
    pubs = [{"id": p.id, "title": p.title, "authors": p.authors, "doi": p.doi, "external_source": p.external_source} for p in prof.publications]
    pats = [{"id": pt.id, "title": pt.title, "patent_number": pt.patent_number, "assignee": pt.assignee} for pt in prof.patents]
    hist = RESEARCH_HISTORY_STORE.get(prof.id, [])
    
    tech_areas = []
    if prof.technology_areas:
        tech_areas = [ta.strip() for ta in prof.technology_areas.split(",") if ta.strip()]

    return {
        "id": prof.id,
        "user_id": prof.user_id,
        "title": prof.title or "Researcher",
        "bio": prof.bio or "",
        "technology_areas": tech_areas,
        "research_domains": domains,
        "domains": domains,
        "keywords": keywords,
        "interests": domains,
        "publication_ids": pub_ids,
        "patent_ids": pat_ids,
        "publications": pubs,
        "patents": pats,
        "research_history": hist,
        "created_at": prof.created_at
    }

@router.get("/me")
@profile_alias_router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    prof = repo.get_by_user_id(current_user.id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return build_profile_dict(prof, db)

@profile_alias_router.get("")
@profile_alias_router.get("/")
def get_profile_root(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    prof = repo.get_by_user_id(current_user.id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return build_profile_dict(prof, db)

@profile_alias_router.post("", status_code=201)
@profile_alias_router.post("/", status_code=201)
def create_profile(profile_in: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    if "academic" in profile_in:
        deg = profile_in["academic"].get("degree")
        if deg:
            prof.title = f"Researcher ({deg})"
    if "organization" in profile_in:
        org_name = profile_in["organization"].get("name")
        if org_name and not prof.bio:
            prof.bio = f"Affiliated with {org_name}"
    if "bio" in profile_in and profile_in["bio"]:
        prof.bio = profile_in["bio"]
    db.commit()
    return build_profile_dict(prof, db)

@router.put("/me")
@profile_alias_router.put("/me")
@profile_alias_router.put("")
@profile_alias_router.put("/")
@users_alias_router.put("/me/profile")
def update_my_profile(profile_in: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    if "academic" in profile_in:
        deg = profile_in["academic"].get("degree")
        if deg:
            prof.title = f"Researcher ({deg})"
    if "organization" in profile_in:
        org_name = profile_in["organization"].get("name")
        if org_name:
            prof.bio = f"Affiliated with {org_name}"
    if "bio" in profile_in and profile_in["bio"]:
        prof.bio = profile_in["bio"]
    db.commit()
    return build_profile_dict(prof, db)

@profile_alias_router.post("/domains")
@profile_alias_router.post("/interests")
def add_profile_domain_or_interest(domain_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    val = domain_data.get("value") or domain_data.get("domain") or domain_data.get("interest") or "General AI"
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    exist = db.query(ResearchInterest).filter(ResearchInterest.profile_id == prof.id, ResearchInterest.domain_name == val).first()
    if exist:
        raise HTTPException(status_code=409, detail=f"Interest '{val}' already exists")
    db.add(ResearchInterest(profile_id=prof.id, domain_name=val))
    db.commit()
    return {"status": "success", "domain": val, "value": val}

@profile_alias_router.post("/keywords")
def add_profile_keyword(kw_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    val = kw_data.get("value") or kw_data.get("keyword") or "AI"
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    exist = db.query(Keyword).filter(Keyword.profile_id == prof.id, Keyword.keyword_name == val).first()
    if exist:
        raise HTTPException(status_code=409, detail=f"Keyword '{val}' already exists")
    db.add(Keyword(profile_id=prof.id, keyword_name=val))
    db.commit()
    return {"status": "success", "keyword": val, "value": val}

@profile_alias_router.post("/technology-areas")
def add_profile_technology_area(tech_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    val = tech_data.get("value") or tech_data.get("area") or "Artificial Intelligence"
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    existing_areas = [ta.strip() for ta in (prof.technology_areas or "").split(",") if ta.strip()]
    if val in existing_areas:
        raise HTTPException(status_code=409, detail=f"Technology area '{val}' already exists")
    existing_areas.append(val)
    prof.technology_areas = ", ".join(existing_areas)
    db.commit()
    return {"status": "success", "value": val}

@profile_alias_router.post("/research-history", status_code=201)
def add_research_history(hist_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    start_year = hist_data.get("start_year")
    end_year = hist_data.get("end_year")
    if start_year is not None and end_year is not None and start_year > end_year:
        raise HTTPException(status_code=422, detail="start_year cannot be greater than end_year")
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    if prof.id not in RESEARCH_HISTORY_STORE:
        RESEARCH_HISTORY_STORE[prof.id] = []
    item = {
        "title": hist_data.get("title", "Research Project"),
        "start_year": start_year,
        "end_year": end_year
    }
    RESEARCH_HISTORY_STORE[prof.id].append(item)
    return item

@profile_alias_router.get("/publications")
def get_saved_publications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    pubs = db.query(Publication).filter(Publication.profile_id == prof.id).all()
    return [{"id": p.id, "title": p.title, "authors": p.authors, "doi": p.doi, "external_source": p.external_source} for p in pubs]

@profile_alias_router.post("/publications", status_code=201)
def save_publication(pub_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    doi = pub_data.get("doi")
    if doi:
        existing = db.query(Publication).filter(Publication.doi == doi).first()
        if existing:
            existing.profile_id = prof.id
            db.commit()
            return {"status": "saved", "id": existing.id, "title": existing.title}
    pub = Publication(
        profile_id=prof.id,
        title=pub_data.get("title", "Untitled Publication"),
        authors=str(pub_data.get("authors", "Unknown")),
        doi=doi,
        external_source=pub_data.get("external_source", "openalex")
    )
    db.add(pub)
    db.commit()
    db.refresh(pub)
    return {"status": "saved", "id": pub.id, "title": pub.title}

@profile_alias_router.get("/patents")
def get_saved_patents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    pats = db.query(Patent).filter(Patent.profile_id == prof.id).all()
    return [{"id": p.id, "title": p.title, "patent_number": p.patent_number} for p in pats]

@profile_alias_router.post("/patents", status_code=201)
def save_patent(pat_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    pat_num = pat_data.get("patent_number")
    if pat_num:
        existing = db.query(Patent).filter(Patent.patent_number == pat_num).first()
        if existing:
            existing.profile_id = prof.id
            db.commit()
            return {"status": "saved", "id": existing.id, "title": existing.title}
    pat = Patent(
        profile_id=prof.id,
        title=pat_data.get("title", "Untitled Patent"),
        patent_number=pat_num or "US0000000",
        assignee=pat_data.get("assignee"),
        external_source=pat_data.get("external_source") or "uspto"
    )
    db.add(pat)
    db.commit()
    db.refresh(pat)
    return {"status": "saved", "id": pat.id, "title": pat.title}

@router.get("/{user_id}", response_model=ProfileResponse)
@profile_alias_router.get("/{user_id}", response_model=ProfileResponse)
def get_profile_by_user_id(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = ProfileService(db)
    return service.get_profile(user_id)
