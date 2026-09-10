import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from models import FundingOpportunity, FundingSource
from main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def seed_ai_grant(db):
    source = FundingSource(name="Integration Test Source", source_type="Government Grants")
    db.add(source)
    db.flush()
    opp = FundingOpportunity(
        source_id=source.id,
        title="AI Research Grant",
        agency="NSF",
        grant_amount=250000,
        deadline=date.today() + timedelta(days=45),
        status="Open",
        research_domain="Artificial Intelligence",
        career_stage="Early-Career",
        eligible_geography="US",
        funding_type="Grant"
    )
    db.add(opp)
    db.commit()
    return opp


def test_full_researcher_workflow(db_session):
    """
    End-to-end: register -> login token -> update profile with a research
    domain -> confirm grant matching finds a relevant opportunity -> confirm
    technology intelligence endpoints work in the same session (no cross-
    module interference).
    """
    seed_ai_grant(db_session)

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(app)

    register_payload = {
        "full_name": "Integration Test User",
        "email": "integration_user@example.com",
        "password": "TestPass123",
        "role": "researcher"
    }
    r_register = client.post("/api/auth/register", json=register_payload)
    assert r_register.status_code == 200
    token = r_register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_payload = {
        "title": "AI Researcher",
        "research_domains": ["Artificial Intelligence"],
        "keywords": ["Deep Learning"]
    }
    r_profile = client.put("/api/profiles/me", json=profile_payload, headers=headers)
    assert r_profile.status_code == 200
    assert r_profile.json()["research_domains"] == ["Artificial Intelligence"]

    r_get_profile = client.get("/api/profiles/me", headers=headers)
    assert r_get_profile.status_code == 200
    assert "Artificial Intelligence" in r_get_profile.json()["research_domains"]

    match_payload = {
        "research_domains": ["Artificial Intelligence"],
        "career_stage": "Early-Career",
        "geography": "US",
        "funding_types": ["Grant"],
        "include_expired": False
    }
    r_match = client.post("/api/grants/match", json=match_payload)
    assert r_match.status_code == 200
    matches = r_match.json()["matched_grants"]
    assert len(matches) >= 1
    assert any(m["opportunity"]["title"] == "AI Research Grant" for m in matches)

    r_tech = client.get("/api/technology/emerging")
    assert r_tech.status_code == 200
    assert len(r_tech.json()) >= 3

    app.dependency_overrides.clear()


def test_unauthenticated_profile_update_rejected(db_session):
    """A profile update without a valid token should be rejected, not silently succeed."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(app)

    r = client.put("/api/profiles/me", json={"research_domains": ["Biotechnology"]})
    assert r.status_code in (401, 403)

    app.dependency_overrides.clear()