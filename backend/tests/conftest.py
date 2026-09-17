import os
os.environ["DATABASE_URL"]="sqlite:///./test_milestone1.db"
os.environ["MONGODB_URL"]="mongodb://localhost:27017"
os.environ["JWT_SECRET"]="test-only-secret-0123456789abcdef0123456789abcdef"
os.environ["PATENTS_PROVIDER"]="local"
os.environ["LOCAL_PATENT_DATASET"]=str((__import__("pathlib").Path(__file__).resolve().parents[2]/"data"/"patents_public_sample.json"))
import pytest
from fastapi.testclient import TestClient

try:
    from main import app
except ImportError:
    from app.main import app

try:
    from app.db.postgres import Base, engine
except ImportError:
    from database import Base, engine

try:
    from app.models.user import User, Role
    from app.models.profile import UserProfile
except ImportError:
    from models import User, Role, ResearchProfile as UserProfile

try:
    from app.core.security import hash_password
except ImportError:
    def hash_password(pwd): return pwd

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c: yield c

def register(client,email='researcher@example.com',password='StrongPass123!'):
    return client.post('/api/v1/auth/register',json={'email':email,'full_name':'Test User','password':password})

def login(client,email='researcher@example.com',password='StrongPass123!'):
    return client.post('/api/v1/auth/login',data={'username':email,'password':password})
