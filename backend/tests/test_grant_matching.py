import sys
import os
import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base
from models import FundingOpportunity, FundingSource, User, ResearchProfile, ResearchInterest

from schemas import GrantMatchRequest, MatchingRulesConfig
from services.grant_matching_service import GrantMatchingRulesEngine

# In-memory SQLite DB for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
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

def create_sample_opportunities(db):
    source = FundingSource(name="Test Source", source_type="Government Grants")
    db.add(source)
    db.flush()

    today = date.today()

    opp1 = FundingOpportunity(
        source_id=source.id,
        title="AI Commercialization Grant",
        agency="NSF",
        grant_amount=1000000,
        deadline=today + timedelta(days=60),
        status="Open",
        research_domain="Artificial Intelligence",
        career_stage="Early-Career",
        eligible_geography="US",
        funding_type="Grant"
    )

    opp2 = FundingOpportunity(
        source_id=source.id,
        title="BioTech Research Fellowship",
        agency="NIH",
        grant_amount=500000,
        deadline=today + timedelta(days=90),
        status="Open",
        research_domain="Biotechnology",
        career_stage="Mid-Career",
        eligible_geography="Global",
        funding_type="Fellowship"
    )

    opp3 = FundingOpportunity(
        source_id=source.id,
        title="Expired Energy Innovation Grant",
        agency="DOE",
        grant_amount=750000,
        deadline=today - timedelta(days=30), # EXPIRED
        status="Expired",
        research_domain="Climate",
        career_stage="Any",
        eligible_geography="Global",
        funding_type="Grant"
    )

    db.add_all([opp1, opp2, opp3])
    db.commit()
    return [opp1, opp2, opp3]


def test_full_grant_match(db_session):
    opps = create_sample_opportunities(db_session)
    engine = GrantMatchingRulesEngine()

    request = GrantMatchRequest(
        research_domains=["Artificial Intelligence"],
        career_stage="Early-Career",
        geography="US",
        funding_types=["Grant"],
        include_expired=False
    )

    res = engine.evaluate_opportunity(opps[0], request)

    assert res.is_eligible is True
    assert res.eligibility_status == "ELIGIBLE"
    assert res.overall_eligibility_score == 100.0
    assert len(res.rejection_reasons) == 0


def test_expired_grant_edge_case(db_session):
    opps = create_sample_opportunities(db_session)
    engine = GrantMatchingRulesEngine()

    request = GrantMatchRequest(
        research_domains=["Climate"],
        career_stage="Any",
        geography="Global",
        funding_types=["Grant"],
        include_expired=False
    )

    res = engine.evaluate_opportunity(opps[2], request)

    assert res.is_eligible is False
    assert res.eligibility_status == "EXPIRED"
    assert "Grant deadline expired" in res.rejection_reasons[0]


def test_geography_mismatch_edge_case(db_session):
    opps = create_sample_opportunities(db_session)
    engine = GrantMatchingRulesEngine()

    # Researcher in India applying for US-only grant
    request = GrantMatchRequest(
        research_domains=["Artificial Intelligence"],
        career_stage="Early-Career",
        geography="India",
        funding_types=["Grant"],
        include_expired=False
    )

    res = engine.evaluate_opportunity(opps[0], request)

    assert res.is_eligible is False
    assert res.eligibility_status == "INELIGIBLE"
    assert any("Geographical restriction" in r for r in res.rejection_reasons)


def test_partial_match_edge_case(db_session):
    opps = create_sample_opportunities(db_session)
    engine = GrantMatchingRulesEngine()

    # Domain matches BioTech, but career stage is Early-Career instead of Mid-Career
    request = GrantMatchRequest(
        research_domains=["Biotechnology"],
        career_stage="Early-Career",
        geography="Global",
        funding_types=["Fellowship"],
        include_expired=False
    )

    res = engine.evaluate_opportunity(opps[1], request)

    assert res.is_eligible is True # Partial match is still eligible
    assert res.eligibility_status in ["PARTIAL_MATCH", "ELIGIBLE"]
    assert res.overall_eligibility_score > 50.0


def test_rule_weight_tuning_without_code_changes(db_session):
    opps = create_sample_opportunities(db_session)
    engine = GrantMatchingRulesEngine()

    # Tune config: Increase domain weight to 80%, reduce geography weight
    new_config = MatchingRulesConfig(
        domain_weight=80.0,
        career_stage_weight=10.0,
        geography_weight=5.0,
        funding_type_weight=5.0,
        strict_geography_check=False
    )
    engine.update_config(new_config)

    request = GrantMatchRequest(
        research_domains=["Artificial Intelligence"],
        career_stage="Mid-Career",
        geography="EU",
        funding_types=["Accelerator"],
        include_expired=False
    )

    res = engine.evaluate_opportunity(opps[0], request)

    # Because domain weight is 80%, domain match boosts score heavily
    assert res.overall_eligibility_score >= 80.0


def test_no_matches_edge_case(db_session):
    opps = create_sample_opportunities(db_session)
    engine = GrantMatchingRulesEngine()

    # Researcher requesting completely non-existent domain and impossible minimum funding amount
    request = GrantMatchRequest(
        research_domains=["Quantum Astrophysics Deep Sea"],
        career_stage="Senior/Lead",
        geography="Antarctica",
        funding_types=["Accelerator"],
        min_amount=10000000, # $10M min amount, none match
        include_expired=False
    )

    # Filter opportunities by min_amount like router does
    filtered_opps = [o for o in opps if o.grant_amount >= request.min_amount]
    results = [engine.evaluate_opportunity(o, request) for o in filtered_opps]

    total_eligible = sum(1 for r in results if r.eligibility_status == "ELIGIBLE")
    assert total_eligible == 0
    assert len(results) == 0


def test_fastapi_grant_matching_endpoints(db_session):
    from fastapi.testclient import TestClient
    from main import app
    from database import get_db

    # Ensure tables and sample data exist in in-memory test database
    create_sample_opportunities(db_session)

    # Override DB dependency
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(app)

    # 1. Test POST /api/grants/match
    match_payload = {
        "research_domains": ["Artificial Intelligence"],
        "career_stage": "Early-Career",
        "geography": "US",
        "funding_types": ["Grant"],
        "include_expired": False
    }
    res = client.post("/api/grants/match", json=match_payload)
    assert res.status_code == 200
    data = res.json()
    assert "total_evaluated" in data
    assert "matched_grants" in data
    assert len(data["matched_grants"]) > 0

    # 2. Test GET /api/grants/matching-rules
    res_rules = client.get("/api/grants/matching-rules")
    assert res_rules.status_code == 200
    rules_data = res_rules.json()
    assert rules_data["domain_weight"] == 35.0

    # 3. Test PUT /api/grants/matching-rules
    new_rules = {
        "domain_weight": 40.0,
        "career_stage_weight": 20.0,
        "geography_weight": 20.0,
        "funding_type_weight": 20.0,
        "min_pass_threshold": 50.0,
        "strict_geography_check": True,
        "strict_deadline_check": True
    }
    res_put = client.put("/api/grants/matching-rules", json=new_rules)
    assert res_put.status_code == 200
    assert res_put.json()["domain_weight"] == 40.0

    # 4. Test GET /api/grants/opportunities
    res_opps = client.get("/api/grants/opportunities")
    assert res_opps.status_code == 200
    assert isinstance(res_opps.json(), list)

    app.dependency_overrides.clear()



