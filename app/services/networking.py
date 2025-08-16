"""
API routes for the Azure Networking service, using a database for persistence
and realistic, structured API paths.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.models import VirtualNetwork
from app.security import verify_token

# Pydantic models for request bodies
from pydantic import BaseModel
class VirtualNetworkCreate(BaseModel):
    location: str
    properties: dict # e.g. {"addressSpace": {"addressPrefixes": ["10.0.0.0/16"]}}

router = APIRouter(
    prefix="/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Network",
    tags=["networking"],
    dependencies=[Depends(verify_token)],
)

@router.put("/virtualNetworks/{vnet_name}", response_model=VirtualNetwork)
def create_or_update_vnet(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    vnet_name: str,
    vnet_body: VirtualNetworkCreate,
):
    """
    Create or update a virtual network (upsert).
    """
    statement = select(VirtualNetwork).where(
        VirtualNetwork.name == vnet_name,
        VirtualNetwork.resource_group == resourceGroupName,
    )
    db_vnet = session.exec(statement).first()

    address_space = vnet_body.properties.get("addressSpace", {}).get("addressPrefixes", [""])[0]

    if db_vnet:
        # Update existing VNet
        db_vnet.location = vnet_body.location
        db_vnet.address_space = address_space
    else:
        # Create new VNet
        db_vnet = VirtualNetwork(
            name=vnet_name,
            resource_group=resourceGroupName,
            location=vnet_body.location,
            address_space=address_space,
        )

    session.add(db_vnet)
    session.commit()
    session.refresh(db_vnet)
    return db_vnet

@router.get("/virtualNetworks/{vnet_name}", response_model=VirtualNetwork)
def get_vnet(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    vnet_name: str,
):
    """
    Get a specific virtual network by name and resource group.
    """
    statement = select(VirtualNetwork).where(
        VirtualNetwork.name == vnet_name,
        VirtualNetwork.resource_group == resourceGroupName,
    )
    vnet = session.exec(statement).first()
    if not vnet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Virtual network not found")
    return vnet

@router.get("/virtualNetworks", response_model=List[VirtualNetwork])
def list_vnets_in_rg(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
):
    """
    List all virtual networks within a specific resource group.
    """
    statement = select(VirtualNetwork).where(VirtualNetwork.resource_group == resourceGroupName)
    vnets = session.exec(statement).all()
    return vnets

@router.delete("/virtualNetworks/{vnet_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vnet(
    *,
    session: Session = Depends(get_session),
    resourceGroupName: str,
    vnet_name: str,
):
    """
    Delete a specific virtual network.
    """
    statement = select(VirtualNetwork).where(
        VirtualNetwork.name == vnet_name,
        VirtualNetwork.resource_group == resourceGroupName,
    )
    vnet_to_delete = session.exec(statement).first()

    if not vnet_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Virtual network not found")

    session.delete(vnet_to_delete)
    session.commit()
    return None
