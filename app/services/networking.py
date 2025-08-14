"""
API routes for the Azure Networking service, using a database for persistence.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.models import VirtualNetwork
from app.security import verify_token

router = APIRouter(
    prefix="/networking",
    tags=["networking"],
    dependencies=[Depends(verify_token)],
)

@router.post("/virtualnetworks/", response_model=VirtualNetwork)
def create_virtual_network(
    *,
    session: Session = Depends(get_session),
    vnet: VirtualNetwork
):
    """
    Create a new virtual network resource in the database.
    """
    # In a real implementation, we would handle subnets and other properties.
    # For now, we just create the main VNet record.
    session.add(vnet)
    session.commit()
    session.refresh(vnet)
    return vnet

@router.get("/virtualnetworks/", response_model=List[VirtualNetwork])
def list_virtual_networks(
    *,
    session: Session = Depends(get_session)
):
    """
    List all virtual network resources in the database.
    """
    vnets = session.exec(select(VirtualNetwork)).all()
    return vnets

@router.get("/virtualnetworks/{vnet_id}", response_model=VirtualNetwork)
def get_virtual_network_by_id(
    *,
    session: Session = Depends(get_session),
    vnet_id: int
):
    """
    Retrieve a virtual network by its database ID.
    """
    vnet = session.get(VirtualNetwork, vnet_id)
    if not vnet:
        raise HTTPException(status_code=404, detail="Virtual network not found")
    return vnet
