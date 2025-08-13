"""
Main FastAPI application for the Azure Emulator.

This module contains the application factory function for creating the
FastAPI application instance.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import create_engine

from app.services import compute, networking, storage
from app.db import create_db_and_tables
from app.config import get_settings

def create_app() -> FastAPI:
    """
    Application factory. Creates and configures the FastAPI app instance.
    This pattern allows for creating separate app instances for production and testing.
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Handles application startup and shutdown events.
        On startup, it creates the settings, the database engine, and the tables.
        The engine is stored in the application state to be accessible by dependencies.
        """
        print("--- Application starting up ---")
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL, echo=True)
        app.state.engine = engine

        print("Creating database and tables...")
        create_db_and_tables(engine)
        print("Database and tables created successfully.")
        yield
        print("--- Application shutting down ---")

    app = FastAPI(
        title="Azure Emulator",
        description="A mock server for the Azure REST API, designed for local development and testing.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Include the routers from the service modules.
    app.include_router(compute.router)
    app.include_router(networking.router)
    app.include_router(storage.router)

    @app.get("/", tags=["Root"])
    def read_root():
        """
        Root endpoint providing a welcome message.
        """
        return {"message": "Welcome to the Azure Emulator"}

    return app
