import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.database import Base, get_db
from app.core.security import create_access_token
from app.db.models import User, RoleEnum

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    yield engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # We must also override get_db here so the API uses the same session
    def _override_get_db():
        yield session
    app.dependency_overrides[get_db] = _override_get_db
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c

from app.core.security import get_password_hash

@pytest.fixture(scope="function")
def admin_user(db_session):
    user = User(email="admin_test@bank.com", hashed_password=get_password_hash("admin123"), full_name="Admin", role=RoleEnum.ADMIN)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def BANK_EMPLOYEE_user(db_session):
    user = User(email="inv_test@bank.com", hashed_password=get_password_hash("admin123"), full_name="Inv", role=RoleEnum.BANK_EMPLOYEE)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def admin_token(admin_user):
    return create_access_token(data={"sub": admin_user.email})

@pytest.fixture(scope="function")
def BANK_EMPLOYEE_token(BANK_EMPLOYEE_user):
    return create_access_token(data={"sub": BANK_EMPLOYEE_user.email})

@pytest.fixture(scope="function")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="function")
def BANK_EMPLOYEE_headers(BANK_EMPLOYEE_token):
    return {"Authorization": f"Bearer {BANK_EMPLOYEE_token}"}
