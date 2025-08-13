"""
Database management module.

This module is refactored to support dependency injection for the database
engine and sessions, making the application more testable.
"""
from fastapi import Request
from sqlmodel import Session, SQLModel

def create_db_and_tables(engine):
    """
    Creates all tables defined by SQLModel models using the provided engine.
    """
    SQLModel.metadata.create_all(engine)

def get_session(request: Request):
    """
    FastAPI dependency to get a database session.

    This function depends on the database engine being available in the
    application state (`request.app.state.engine`), which is set up
    during the application's lifespan event.
    """
    engine = request.app.state.engine
    with Session(engine) as session:
        yield session
