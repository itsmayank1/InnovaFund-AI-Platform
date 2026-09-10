import os
import sys
import logging

# Ensure backend directory is in python sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config import settings
from database import engine, SessionLocal, get_mongo_db
from models import Base, Role, User, Organization
from auth import hash_password
from routers import auth_routes, profile_routes, dataset_routes, admin_routes, grant_matching_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create PostgreSQL database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Research Funding & Innovation Intelligence Platform API (Milestone 2)",
    version=settings.VERSION,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under standard API prefix
app.include_router(auth_routes.router, prefix=settings.API_PREFIX)
app.include_router(profile_routes.router, prefix=settings.API_PREFIX)
app.include_router(dataset_routes.router, prefix=settings.API_PREFIX)
app.include_router(admin_routes.router, prefix=settings.API_PREFIX)
app.include_router(grant_matching_routes.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def startup_db_seed():
    db = SessionLocal()
    try:
        # Seed default roles
        roles = [
            ("researcher", "Academic & Industry Scientists"),
            ("startup_founder", "Tech Entrepreneurs & DeepTech Founders"),
            ("innovation_manager", "University Tech Transfer & R&D Directors"),
            ("administrator", "Platform IT Administrators")
        ]
        for role_name, desc in roles:
            existing = db.query(Role).filter(Role.name == role_name).first()
            if not existing:
                db.add(Role(name=role_name, description=desc))
        
        # Seed default admin account
        admin = db.query(User).filter(User.email == "admin@researchsphere.ai").first()
        if not admin:
            admin = User(
                full_name="Platform Administrator",
                email="admin@researchsphere.ai",
                password_hash=hash_password("Admin@123456"),
                role="administrator",
                is_active=True
            )

            db.add(admin)
        db.commit()
    except Exception as e:
        logger.warning(f"Startup DB seed exception: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    health = {"status": "ok", "postgres": "disconnected", "mongodb": "disconnected"}
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health["postgres"] = "connected"
    except Exception as e:
        health["postgres"] = f"error: {str(e)}"

    mongo = get_mongo_db()
    if mongo is not None:
        try:
            mongo.command("ping")
            health["mongodb"] = "connected"
        except Exception as e:
            health["mongodb"] = f"error: {str(e)}"

    return health