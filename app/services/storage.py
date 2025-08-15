"""
API routes for the Azure Storage service, using a database for persistence.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.models import StorageAccount
from app.security import verify_token

router = APIRouter(
    prefix="/storage",
    tags=["storage"],
    dependencies=[Depends(verify_token)],
)

@router.post("/storageaccounts/", response_model=StorageAccount)
def create_storage_account(
    *,
    session: Session = Depends(get_session),
    account: StorageAccount
):
    """
    Create a new storage account resource in the database.
    """
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.get("/storageaccounts/", response_model=List[StorageAccount])
def list_storage_accounts(
    *,
    session: Session = Depends(get_session)
):
    """
    List all storage account resources in the database.
    """
    accounts = session.exec(select(StorageAccount)).all()
    return accounts

@router.get("/storageaccounts/{account_id}", response_model=StorageAccount)
def get_storage_account_by_id(
    *,
    session: Session = Depends(get_session),
    account_id: int
):
    """
    Retrieve a storage account by its database ID.
    """
    account = session.get(StorageAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Storage account not found")
    return account
