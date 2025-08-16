"""
API routes for the Azure Storage service, using a database for persistence
and realistic, structured API paths.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.models import StorageAccount
from app.security import verify_token

# Pydantic models for request bodies
from pydantic import BaseModel
class Sku(BaseModel):
    name: str

class StorageAccountCreate(BaseModel):
    location: str
    sku: Sku
    kind: str

router = APIRouter(
    prefix="/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Storage",
    tags=["storage"],
    dependencies=[Depends(verify_token)],
)

@router.put("/storageAccounts/{account_name}", response_model=StorageAccount)
def create_or_update_storage_account(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    account_name: str,
    account_body: StorageAccountCreate,
):
    """
    Create or update a storage account (upsert).
    """
    statement = select(StorageAccount).where(
        StorageAccount.name == account_name,
        StorageAccount.resource_group == resourceGroupName,
    )
    db_account = session.exec(statement).first()

    if db_account:
        # Update existing account
        db_account.location = account_body.location
        db_account.sku = account_body.sku.name
        db_account.kind = account_body.kind
    else:
        # Create new account
        db_account = StorageAccount(
            name=account_name,
            resource_group=resourceGroupName,
            location=account_body.location,
            sku=account_body.sku.name,
            kind=account_body.kind,
        )

    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account

@router.get("/storageAccounts/{account_name}", response_model=StorageAccount)
def get_storage_account(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    account_name: str,
):
    """
    Get a specific storage account by name and resource group.
    """
    statement = select(StorageAccount).where(
        StorageAccount.name == account_name,
        StorageAccount.resource_group == resourceGroupName,
    )
    account = session.exec(statement).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage account not found")
    return account

@router.get("/storageAccounts", response_model=List[StorageAccount])
def list_storage_accounts_in_rg(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
):
    """
    List all storage accounts within a specific resource group.
    """
    statement = select(StorageAccount).where(StorageAccount.resource_group == resourceGroupName)
    accounts = session.exec(statement).all()
    return accounts

@router.delete("/storageAccounts/{account_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_storage_account(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    account_name: str,
):
    """
    Delete a specific storage account.
    """
    statement = select(StorageAccount).where(
        StorageAccount.name == account_name,
        StorageAccount.resource_group == resourceGroupName,
    )
    account_to_delete = session.exec(statement).first()

    if not account_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage account not found")

    session.delete(account_to_delete)
    session.commit()
    return None
