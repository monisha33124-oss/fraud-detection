import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import User, RoleEnum
from app.core.security import get_password_hash
import uuid

# Use sqlite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test users
    admin = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin",
        role=RoleEnum.ADMIN
    )
    employee = User(
        email="employee@test.com",
        hashed_password=get_password_hash("employee123"),
        full_name="Employee",
        role=RoleEnum.BANK_EMPLOYEE
    )
    db.add(admin)
    db.add(employee)
    db.commit()
    
    yield
    
    Base.metadata.drop_all(bind=engine)
    db.close()

def test_admin_login():
    response = client.post("/api/v1/auth/login", data={"username": "admin@test.com", "password": "admin123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_employee_login():
    response = client.post("/api/v1/auth/login", data={"username": "employee@test.com", "password": "employee123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_wrong_password_lockout():
    # Attempt 5 wrong logins
    for _ in range(5):
        response = client.post("/api/v1/auth/login", data={"username": "employee@test.com", "password": "wrong"})
        assert response.status_code == 400
        
    # The 6th should be 429
    response = client.post("/api/v1/auth/login", data={"username": "employee@test.com", "password": "wrong"})
    assert response.status_code == 429

def test_unauthenticated():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_admin_accessing_restricted():
    # Login admin
    res = client.post("/api/v1/auth/login", data={"username": "admin@test.com", "password": "admin123"})
    token = res.json()["access_token"]
    
    # Access audit logs (admin only)
    response = client.get("/api/v1/audit/", headers={"Authorization": f"Bearer {token}"})
    # Might be 200 or 404 depending on if there are logs, but not 401/403
    assert response.status_code != 401
    assert response.status_code != 403

def test_employee_accessing_restricted():
    # Create another employee to not hit lockout
    db = TestingSessionLocal()
    emp2 = User(email="emp2@test.com", hashed_password=get_password_hash("emp123"), full_name="E2", role=RoleEnum.BANK_EMPLOYEE)
    db.add(emp2)
    db.commit()
    
    res = client.post("/api/v1/auth/login", data={"username": "emp2@test.com", "password": "emp123"})
    token = res.json()["access_token"]
    
    # Access audit logs (admin only)
    response = client.get("/api/v1/audit/", headers={"Authorization": f"Bearer {token}"})
    # Should be 403
    assert response.status_code == 403

def test_expired_token():
    # Hard to test easily without mocking, but if we create a token manually with exp in the past
    from app.core.security import create_access_token
    from datetime import timedelta
    expired_token = create_access_token({"sub": "admin@test.com"}, expires_delta=timedelta(minutes=-10))
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
