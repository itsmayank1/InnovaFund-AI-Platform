import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from models import PatentRecord
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


def seed_patents(db):
    patents = [
        PatentRecord(
            title="Generative AI Text Model",
            assignee="OpenMind Labs",
            filing_date=date(2023, 3, 15),
            classification="G06N",
            technology_domain="Artificial Intelligence",
            citation_count=120,
            abstract="A method for generating text using transformer architectures."
        ),
        PatentRecord(
            title="Quantum Error Correction Circuit",
            assignee="QuantumCore Inc",
            filing_date=date(2022, 7, 1),
            classification="H03K",
            technology_domain="Quantum Computing",
            citation_count=45,
            abstract="A circuit design for reducing decoherence in qubit arrays."
        ),
        PatentRecord(
            title="Neural Network Compression Method",
            assignee="OpenMind Labs",
            filing_date=date(2023, 11, 20),
            classification="G06N",
            technology_domain="Artificial Intelligence",
            citation_count=8,
            abstract="A pruning technique for reducing model size without accuracy loss."
        ),
    ]
    db.add_all(patents)
    db.commit()
    return patents


def _override_get_db(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    return _get_db


def test_patent_search_by_keyword(db_session):
    seed_patents(db_session)
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    client = TestClient(app)

    r = client.get("/api/patents/search?keyword=neural")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["results"][0]["title"] == "Neural Network Compression Method"

    app.dependency_overrides.clear()


def test_patent_search_by_domain_includes_patent_strength(db_session):
    seed_patents(db_session)
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    client = TestClient(app)

    r = client.get("/api/patents/search?domain=Artificial Intelligence")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2
    for item in data["results"]:
        assert "patent_strength" in item
        assert 0.0 <= item["patent_strength"] <= 1.0

    # The higher-citation, more recent AI patent should score higher than the low-citation one
    by_title = {item["title"]: item["patent_strength"] for item in data["results"]}
    assert by_title["Generative AI Text Model"] > by_title["Neural Network Compression Method"]

    app.dependency_overrides.clear()


def test_patent_clusters_group_by_domain(db_session):
    seed_patents(db_session)
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    client = TestClient(app)

    r = client.get("/api/patents/clusters")
    assert r.status_code == 200
    data = r.json()
    assert data["cluster_count"] == 2

    domains = {c["technology_domain"]: c["patent_count"] for c in data["clusters"]}
    assert domains["Artificial Intelligence"] == 2
    assert domains["Quantum Computing"] == 1

    app.dependency_overrides.clear()


def test_patent_trends_by_year(db_session):
    seed_patents(db_session)
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    client = TestClient(app)

    r = client.get("/api/patents/trends")
    assert r.status_code == 200
    data = r.json()
    assert data["trend_count"] >= 2

    years = {t["year"] for t in data["trends"]}
    assert 2022 in years
    assert 2023 in years

    app.dependency_overrides.clear()


def test_patent_search_no_results_for_unmatched_keyword(db_session):
    seed_patents(db_session)
    app.dependency_overrides[get_db] = _override_get_db(db_session)
    client = TestClient(app)

    r = client.get("/api/patents/search?keyword=nonexistentxyz123")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 0
    assert data["results"] == []

    app.dependency_overrides.clear()