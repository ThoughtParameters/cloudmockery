"""
Pytest configuration and fixtures for the test suite.

This file sets the APP_ENV to 'test' to ensure the application uses
a test-specific configuration. It then sets up an isolated, in-memory
database for the test session.
"""
import os
os.environ['APP_ENV'] = 'test'

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.db import get_session
from app.config import get_settings
from app.models import VirtualMachine  # Ensure models are registered

@pytest.fixture(name="client")
def client_fixture():
    """
    Creates a fully isolated test environment for each test function.
    """
    # Use an in-memory SQLite database with a static connection pool.
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

    app = create_app()
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(name="auth_headers")
def auth_headers_fixture():
    """
    Returns valid authorization headers using the test token.
    This works because get_settings() is now returning the test settings.
    """
    settings = get_settings()
    return {"Authorization": f"Bearer {settings.MOCK_AUTH_TOKEN}"}
