import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, SessionLocal

# Test database setup
TEST_DATABASE_URL = "postgresql://user:password@0.0.0.0:5432/test_company_db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    # Override the database dependency to use the test session
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[SessionLocal] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

