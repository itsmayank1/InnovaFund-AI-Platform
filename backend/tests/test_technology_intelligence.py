import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import get_db
from main import app
from models import Base
from services.technology_intelligence_service import (
    TechnologyIntelligenceService,
    seed_technology_intelligence_if_empty
)

# In-memory SQLite for fast testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_technology_intelligence_if_empty(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_technology_intelligence_service_emerging():
    db = TestingSessionLocal()
    service = TechnologyIntelligenceService(db)
    emerging = service.get_emerging_technologies()
    
    assert len(emerging) >= 3
    assert emerging[0].name == "Generative AI & Agentic Architectures"
    assert emerging[0].growth_rate_pct == 58.4
    assert emerging[0].is_emerging is True
    db.close()


def test_technology_intelligence_maturity_score():
    db = TestingSessionLocal()
    service = TechnologyIntelligenceService(db)
    maturities = service.get_technology_maturity("Quantum Error Correction")
    
    assert len(maturities) == 1
    assert maturities[0].domain_name == "Quantum Error Correction & Hardware"
    assert maturities[0].lifecycle_stage == "Emerging"
    assert maturities[0].trl_level == 4
    assert maturities[0].maturity_score == 64.0
    assert maturities[0].weighted_contribution == 9.6 # 64.0 * 0.15 = 9.6 pts
    db.close()



def test_technology_competitor_tracking():
    db = TestingSessionLocal()
    service = TechnologyIntelligenceService(db)
    competitors = service.get_competitors("Generative AI")
    
    assert len(competitors) == 3
    top_competitor = competitors[0]
    assert top_competitor.assignee_name == "Google DeepMind"
    assert top_competitor.patent_holdings == 420
    assert top_competitor.market_share_pct == 29.5
    db.close()


def test_fastapi_technology_endpoints():
    client = TestClient(app)
    
    # 1. Test /api/technology/emerging
    response = client.get("/api/technology/emerging")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["name"] == "Generative AI & Agentic Architectures"
    
    # 2. Test /api/technology/maturity
    response_mat = client.get("/api/technology/maturity?domain_name=Quantum")
    assert response_mat.status_code == 200
    mat_data = response_mat.json()
    assert len(mat_data) == 1
    assert mat_data[0]["maturity_score"] == 64.0

    # 3. Test /api/technology/competitors
    response_comp = client.get("/api/technology/competitors?domain_name=Generative")
    assert response_comp.status_code == 200
    comp_data = response_comp.json()
    assert len(comp_data) == 3
    assert comp_data[0]["assignee_name"] == "Google DeepMind"
