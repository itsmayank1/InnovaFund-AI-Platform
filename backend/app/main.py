from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, profile
from app.db.session import Base, engine
from app.models import user, research_profile  # noqa: ensures models are registered

app = FastAPI(title="InnovaFund AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])

@app.get("/health")
def health_check():
    return {"status": "ok"}