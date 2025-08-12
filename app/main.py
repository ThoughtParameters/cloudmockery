"""
Main FastAPI application for the Azure Emulator.

This module initializes the FastAPI application and includes the routers
from the different service modules.
"""
from fastapi import FastAPI
from app.services import compute, networking, storage

app = FastAPI(
    title="Azure Emulator",
    description="A mock server for the Azure REST API, designed for local development and testing.",
    version="0.1.0",
)

# Include the routers from the service modules.
# Each router has its own prefix, so they will be mounted under
# /compute, /networking, and /storage respectively.
app.include_router(compute.router)
app.include_router(networking.router)
app.include_router(storage.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint providing a welcome message.
    """
    return {"message": "Welcome to the Azure Emulator"}
