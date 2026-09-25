from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import ProfileResponse, ProfileUpdate
from services.profile_service import ProfileService
from dependencies import get_current_user
from models import User, ResearchProfile, ResearchInterest, Keyword, Publication, Patent
from repositories.profile_repository import ProfileRepository

router = APIRouter(prefix="/profiles", tags=["Research Profile Management"])
profile_alias_router = APIRouter(prefix="/profile", tags=["Research Profile Management"])

@router.get("/me", response_model=ProfileResponse)
@profile_alias_router.get("/me", response_model=ProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = ProfileService(db)
    return service.get_profile(current_user.id)

@router.put("/me", response_model=ProfileResponse)
@profile_alias_router.put("/me", response_model=ProfileResponse)
@profile_alias_router.post("", response_model=ProfileResponse)
@profile_alias_router.post("/", response_model=ProfileResponse)
def update_my_profile(profile_in: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = ProfileService(db)
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
    db.commit()
    return service.get_profile(current_user.id)

@profile_alias_router.post("/domains")
def add_profile_domain(domain_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    val = domain_data.get("value") or domain_data.get("domain") or "General AI"
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    exist = db.query(ResearchInterest).filter(ResearchInterest.profile_id == prof.id, ResearchInterest.domain_name == val).first()
    if not exist:
        db.add(ResearchInterest(profile_id=prof.id, domain_name=val))
        db.commit()
    return {"status": "success", "domain": val}

@profile_alias_router.post("/keywords")
def add_profile_keyword(kw_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    val = kw_data.get("value") or kw_data.get("keyword") or "AI"
    repo = ProfileRepository(db)
    prof = repo.get_or_create(current_user.id)
    exist = db.query(Keyword).filter(Keyword.profile_id == prof.id, Keyword.keyword_name == val).first()
    if not exist:
        db.add(Keyword(profile_id=prof.id, keyword_name=val))
        db.commit()
    return {"status": "success", "keyword": val}

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
        external_source=pub_data.get("external_source", "local")
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
        assignee=pat_data.get("assignee")
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
