"""
Pytest configuration and fixtures for the test suite.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.db import get_session
from app.models import VirtualMachine  # Ensure models are registered

@pytest.fixture(name="client")
def client_fixture():
    """
    Creates a fully isolated test environment for each test function.
    """
    # Use an in-memory SQLite database with a static connection pool.
    # This ensures the same in-memory database is used for the entire
    # test function, preserving tables and data.
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    def get_session_override():
        """Override the application's get_session dependency."""
        with Session(test_engine) as session:
            yield session

    # Create a new app instance for this test run.
    app = create_app()
    # Override the production database dependency with the test database.
    app.dependency_overrides[get_session] = get_session_override

    # Create a client to interact with the test app.
    client = TestClient(app)
    yield client

    # Clean up the override and the database tables.
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)
