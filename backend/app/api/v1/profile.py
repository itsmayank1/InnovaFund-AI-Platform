from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.schemas.research_profile import ResearchProfileCreate, ResearchProfileOut
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=ResearchProfileOut)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == current_user.id).first()
    if not profile:
        profile = ResearchProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/me", response_model=ResearchProfileOut)
def update_my_profile(
    payload: ResearchProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == current_user.id).first()
    if not profile:
        profile = ResearchProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile